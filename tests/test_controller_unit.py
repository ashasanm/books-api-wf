"""
Unit tests for the BookController layer.

BookService is fully mocked — tests focus on HTTP error translation.
"""

import pytest
from unittest.mock import patch
from fastapi import HTTPException
from botocore.exceptions import ClientError

from app.schemas import BookCreate
from app.controllers.books import BookController

VALID_BOOK = BookCreate(
    id="/books/id1",
    author="/authors/id1",
    name="Fancy Tech",
    note="Awesome book for beginners in Fancy.",
    serial="C040102",
)


class TestBookControllerCreate:
    def test_create_succeeds_without_exception(self):
        with patch("app.controllers.books.BookService.create_book") as mock:
            mock.return_value = None
            BookController.create_book(VALID_BOOK)  # should not raise

    def test_create_raises_400_on_duplicate(self):
        with patch("app.controllers.books.BookService.create_book") as mock:
            mock.side_effect = ValueError("Book with id 'id1' already exists.")

            with pytest.raises(HTTPException) as exc_info:
                BookController.create_book(VALID_BOOK)

        assert exc_info.value.status_code == 400
        assert "already exists" in exc_info.value.detail

    def test_create_raises_500_on_client_error(self):
        error_response = {"Error": {"Code": "ProvisionedThroughputExceededException", "Message": ""}}
        with patch("app.controllers.books.BookService.create_book") as mock:
            mock.side_effect = ClientError(error_response, "PutItem")

            with pytest.raises(HTTPException) as exc_info:
                BookController.create_book(VALID_BOOK)

        assert exc_info.value.status_code == 500

    def test_create_raises_500_on_unexpected_error(self):
        with patch("app.controllers.books.BookService.create_book") as mock:
            mock.side_effect = RuntimeError("boom")

            with pytest.raises(HTTPException) as exc_info:
                BookController.create_book(VALID_BOOK)

        assert exc_info.value.status_code == 500


class TestBookControllerGet:
    def test_get_returns_book_dict(self):
        expected = VALID_BOOK.model_dump()
        with patch("app.controllers.books.BookService.get_book") as mock:
            mock.return_value = expected
            result = BookController.get_book("id1")

        assert result == expected

    def test_get_raises_404_when_not_found(self):
        with patch("app.controllers.books.BookService.get_book") as mock:
            mock.return_value = None

            with pytest.raises(HTTPException) as exc_info:
                BookController.get_book("nonexistent")

        assert exc_info.value.status_code == 404
        assert "nonexistent" in exc_info.value.detail

    def test_get_raises_500_on_client_error(self):
        error_response = {"Error": {"Code": "InternalServerError", "Message": ""}}
        with patch("app.controllers.books.BookService.get_book") as mock:
            mock.side_effect = ClientError(error_response, "GetItem")

            with pytest.raises(HTTPException) as exc_info:
                BookController.get_book("id1")

        assert exc_info.value.status_code == 500

    def test_get_raises_500_on_unexpected_error(self):
        with patch("app.controllers.books.BookService.get_book") as mock:
            mock.side_effect = RuntimeError("unexpected")

            with pytest.raises(HTTPException) as exc_info:
                BookController.get_book("id1")

        assert exc_info.value.status_code == 500

    def test_get_passes_correct_id_to_service(self):
        with patch("app.controllers.books.BookService.get_book") as mock:
            mock.return_value = VALID_BOOK.model_dump()
            BookController.get_book("id99")

        mock.assert_called_once_with("id99")