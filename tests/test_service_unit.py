"""
Unit tests for the BookService layer.

BookRepository is fully mocked — no AWS credentials or network needed.
"""

import pytest
from unittest.mock import patch, MagicMock
from botocore.exceptions import ClientError

from app.schemas import BookCreate
from app.services.books import BookService

VALID_BOOK = BookCreate(
    id="/books/id1",
    author="/authors/id1",
    name="Fancy Tech",
    note="Awesome book for beginners in Fancy.",
    serial="C040102",
)


class TestBookServiceCreate:
    def test_create_delegates_to_repository(self):
        with patch("app.services.books.book_repository.create") as mock_create:
            mock_create.return_value = None
            BookService.create_book(VALID_BOOK)

        mock_create.assert_called_once_with(VALID_BOOK.model_dump())

    def test_create_propagates_value_error_on_duplicate(self):
        with patch("app.services.books.book_repository.create") as mock_create:
            mock_create.side_effect = ValueError("Book with id 'id1' already exists.")

            with pytest.raises(ValueError, match="already exists"):
                BookService.create_book(VALID_BOOK)

    def test_create_propagates_client_error(self):
        error_response = {"Error": {"Code": "ProvisionedThroughputExceededException", "Message": ""}}
        with patch("app.services.books.book_repository.create") as mock_create:
            mock_create.side_effect = ClientError(error_response, "PutItem")

            with pytest.raises(ClientError):
                BookService.create_book(VALID_BOOK)


class TestBookServiceGet:
    def test_get_returns_book_dict(self):
        expected = VALID_BOOK.model_dump()
        with patch("app.services.books.book_repository.get") as mock_get:
            mock_get.return_value = expected
            result = BookService.get_book("id1")

        assert result == expected
        mock_get.assert_called_once_with("id1")

    def test_get_returns_none_when_not_found(self):
        with patch("app.services.books.book_repository.get") as mock_get:
            mock_get.return_value = None
            result = BookService.get_book("missing")

        assert result is None

    def test_get_propagates_client_error(self):
        error_response = {"Error": {"Code": "InternalServerError", "Message": ""}}
        with patch("app.services.books.book_repository.get") as mock_get:
            mock_get.side_effect = ClientError(error_response, "GetItem")

            with pytest.raises(ClientError):
                BookService.get_book("id1")