from pydantic import BaseModel, Field
from typing import TypedDict
from pymongo.asynchronous.collection import AsyncCollection
from ..db import database
from typing import List, Optional


class Review(BaseModel):
    page: int
    review: str


class FileSchema(TypedDict):
    name: str = Field(..., description="Name of the file")
    status: str = Field(..., description="Status of the file")
    reviews: Optional[List[Review]] = None

 
COLLECTION_NAME = "files"
files_collection: AsyncCollection = database[COLLECTION_NAME]