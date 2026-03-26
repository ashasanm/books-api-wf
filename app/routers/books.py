import logging
from fastapi import APIRouter, HTTPException, status
from botocore.exceptions import ClientError

from app.schemas import BookCreate, BookResponse
from app import repository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/books", tags=["books"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Create a new book",
    responses={
        201: {"description": "Book created successfully"},
        400: {"description": "Bad request – missing or invalid fields"},
        500: {"description": "Internal server error"},
    },
)
def create_book(book: BookCreate):
    """
    Persist a new book record.

    - Returns **201 Created** on success.
    - Returns **400 Bad Request** if any required field is absent or if the
      book id already exists.
    - Returns **500 Internal Server Error** on unexpected failures.
    """
    try:
        repository.create_book(book.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except ClientError as exc:
        logger.exception("DynamoDB error while creating book")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again later.",
        )
    except Exception as exc:
        logger.exception("Unexpected error while creating book")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again later.",
        )


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
    """
    Fetch a book by its short id (e.g. `id1`).

    - Returns **200 OK** with the book payload on success.
    - Returns **404 Not Found** if no book matches the given id.
    - Returns **500 Internal Server Error** on unexpected failures.
    """
    try:
        item = repository.get_book(book_id)
    except ClientError:
        logger.exception("DynamoDB error while fetching book '%s'", book_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again later.",
        )
    except Exception:
        logger.exception("Unexpected error while fetching book '%s'", book_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again later.",
        )

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id '{book_id}' was not found.",
        )
    return item
