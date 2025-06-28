import os
from ..db.collections.files import files_collection
from bson import ObjectId
from pdf2image import convert_from_path
import google.generativeai as genai
from dotenv import load_dotenv


load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel(model_name="gemini-1.5-flash")  


async def process_file(id: str, file_path: str):
    await files_collection.update_one({"_id": ObjectId(id)}, {
        "$set": {"status": "processing"}
    })

    await files_collection.update_one({"_id": ObjectId(id)}, {
        "$set": {"status": "converting to images"}
    })

    pages = convert_from_path(file_path)
    image_folder_path = f"/mnt/uploads/images/{id}"
    os.makedirs(image_folder_path, exist_ok=True)

    reviews = []

    # Prompt for resume review
    resume_review_prompt = (
        "You are a resume reviewer. Analyze this resume and provide :\n"
        "1. Review the resume and list key strength.\n"
        "2. Areas for improvement.\n"
        "3. Suggestions to enhance the resume.\n"
        "4. Give the rating and recommended job"
    )

    for i, page in enumerate(pages):
        image_save_path = f"{image_folder_path}/image-{i}.jpg"
        page.save(image_save_path, 'JPEG')

        # Read and send image to Gemini
        with open(image_save_path, "rb") as img_file:
            try:
                response = model.generate_content(
                    [
                        {"mime_type": "image/jpeg", "data": img_file.read()},
                        {"text": resume_review_prompt}
                    ]
                )
                review_text = response.text
            except Exception as e:
                review_text = f"Error processing page {i}: {str(e)}"

            reviews.append({
                "page": i,
                "review": review_text
            })

    await files_collection.update_one({"_id": ObjectId(id)}, {
        "$set": {
            "status": "resume review complete",
            "reviews": reviews
        }
    })
