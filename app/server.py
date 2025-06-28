from fastapi import FastAPI, UploadFile, Path, HTTPException
from .utils.file import save_to_disk
from .db.collections.files import files_collection, FileSchema
from .queue.q import q
from .queue.worker import process_file
from bson import ObjectId

app = FastAPI()


def convert_objectid_to_str(doc):
    """
    Recursively convert ObjectId fields to strings in the document or dict.
    """
    if isinstance(doc, dict):
        return {k: convert_objectid_to_str(v) for k, v in doc.items()}
    elif isinstance(doc, list):
        return [convert_objectid_to_str(i) for i in doc]
    elif isinstance(doc, ObjectId):
        return str(doc)
    else:
        return doc


@app.get("/")
def hello():
    return {"status": "healthy on port 8000"}


@app.get("/{id}")
async def get_file_id(id: str = Path(..., description="Id of the file")):
    db_file = await files_collection.find_one({"_id": ObjectId(id)})
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")

    # Convert ObjectId(s) to strings
    db_file = convert_objectid_to_str(db_file)

    return {
        "_id": db_file["_id"],
        "name": db_file.get("name"),
        "status": db_file.get("status"),
        "reviews": db_file.get("reviews"),
    }


@app.post("/upload")
async def upload_file(file: UploadFile):
    db_file = await files_collection.insert_one(
        document=FileSchema(
            name=file.filename,
            status="saving"
        )
    )

    file_path = f"/mnt/uploads/{str(db_file.inserted_id)}/{file.filename}"

    await save_to_disk(file=await file.read(), path=file_path)

    q.enqueue(process_file, str(db_file.inserted_id), file_path)

    await files_collection.update_one({"_id": db_file.inserted_id}, {
        "$set": {
            "status": "queued"
        }
    })

    return {"file_id": str(db_file.inserted_id)}
