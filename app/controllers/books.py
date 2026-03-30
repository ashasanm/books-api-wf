import logging
from fastapi import HTTPException, status
from botocore.exceptions import ClientError

from app.services.books import BookService
from app.schemas import BookCreate

logger = logging.getLogger(__name__)


class BookController:
    """Handles HTTP-level concerns: error translation, logging, HTTP exceptions."""

    @staticmethod
    def create_book(book: BookCreate) -> None:
        try:
            BookService.create_book(book)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
        except ClientError:
            logger.exception("DynamoDB error while creating book")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred. Please try again later.",
            )
        except Exception:
            logger.exception("Unexpected error while creating book")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred. Please try again later.",
            )

    @staticmethod
    def get_book(book_id: str) -> dict:
        try:
            item = BookService.get_book(book_id)
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