from pydantic import BaseModel, Field


class BookCreate(BaseModel):
    id: str = Field(..., description="Resource path, e.g. /books/id1")
    author: str = Field(..., description="Author resource path, e.g. /authors/id1")
    name: str = Field(..., description="Title of the book")
    note: str = Field(..., description="Short description or note about the book")
    serial: str = Field(..., description="Serial / ISBN-style identifier")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "/books/id1",
                "author": "/authors/id1",
                "name": "Fancy Tech",
                "note": "Awesome book for beginners in Fancy.",
                "serial": "C040102",
            }
        }
    }


class BookResponse(BookCreate):
    pass
