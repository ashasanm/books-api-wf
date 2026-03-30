from app.repository import book_repository
from app.schemas import BookCreate


class BookService:
    """Business logic layer for book operations."""

    @staticmethod
    def create_book(book: BookCreate) -> None:
        """
        Validate and persist a new book.

        Raises:
            ValueError: if a book with the same id already exists.
        """
        book_repository.create(book.model_dump())

    @staticmethod
    def get_book(book_id: str) -> dict | None:
        """
        Retrieve a book by its short id.

        Returns:
            The book dict, or None if not found.
        """
        return book_repository.get(book_id)