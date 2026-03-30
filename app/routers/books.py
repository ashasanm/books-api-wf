from fastapi import APIRouter, status

from app.schemas import BookCreate, BookResponse
from app.controllers.books import BookController

router = APIRouter(prefix="/books", tags=["books"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Create a new book",
    responses={
        201: {"description": "Book created successfully"},
        400: {"description": "Bad request - missing or invalid fields"},
        500: {"description": "Internal server error"},
    },
)
def create_book(book: BookCreate):
    BookController.create_book(book)


@router.get(
    "/{book_id}",
    response_model=BookResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve a book by id",
    responses={
        200: {"description": "Book found"},
        404: {"description": "Book not found"},
        500: {"description": "Internal server error"},
    },
)
def get_book(book_id: str):
    return BookController.get_book(book_id)