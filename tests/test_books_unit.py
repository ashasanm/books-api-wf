"""
Unit tests for the /api/books endpoints.

The BookRepository is fully mocked so these tests run without
any AWS credentials or network access.
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from botocore.exceptions import ClientError

from app.main import app

client = TestClient(app)

VALID_BOOK = {
    "id": "/books/id1",
    "author": "/authors/id1",
    "name": "Fancy Tech",
    "note": "Awesome book for beginners in Fancy.",
    "serial": "C040102",
}


# ---------------------------------------------------------------------------
# POST /api/books
# ---------------------------------------------------------------------------


class TestCreateBook:
    def test_create_book_success_returns_201(self):
        with patch("app.routers.books.book_repository.create") as mock_create:
            mock_create.return_value = None
            response = client.post("/api/books", json=VALID_BOOK)

        assert response.status_code == 201

    def test_create_book_missing_field_returns_422(self):
        incomplete = {k: v for k, v in VALID_BOOK.items() if k != "serial"}
        response = client.post("/api/books", json=incomplete)

        assert response.status_code == 422
        assert "serial" in str(response.json())

    def test_create_book_empty_body_returns_422(self):
        response = client.post("/api/books", json={})
        assert response.status_code == 422

    def test_create_book_duplicate_returns_400(self):
        with patch("app.routers.books.book_repository.create") as mock_create:
            mock_create.side_effect = ValueError("Book with id 'id1' already exists.")
            response = client.post("/api/books", json=VALID_BOOK)

        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_create_book_dynamodb_client_error_returns_500(self):
        error_response = {"Error": {"Code": "ProvisionedThroughputExceededException", "Message": "Rate exceeded"}}
        with patch("app.routers.books.book_repository.create") as mock_create:
            mock_create.side_effect = ClientError(error_response, "PutItem")
            response = client.post("/api/books", json=VALID_BOOK)

        assert response.status_code == 500

    def test_create_book_unexpected_error_returns_500(self):
        with patch("app.routers.books.book_repository.create") as mock_create:
            mock_create.side_effect = RuntimeError("boom")
            response = client.post("/api/books", json=VALID_BOOK)

        assert response.status_code == 500

    def test_create_book_calls_repository_with_correct_data(self):
        with patch("app.routers.books.book_repository.create") as mock_create:
            mock_create.return_value = None
            client.post("/api/books", json=VALID_BOOK)

        mock_create.assert_called_once_with(VALID_BOOK)

    def test_create_book_extra_fields_ignored(self):
        payload = {**VALID_BOOK, "unexpected_field": "ignored"}
        with patch("app.routers.books.book_repository.create") as mock_create:
            mock_create.return_value = None
            response = client.post("/api/books", json=payload)

        assert response.status_code == 201


# ---------------------------------------------------------------------------
# GET /api/books/{id}
# ---------------------------------------------------------------------------


class TestGetBook:
    def test_get_book_success_returns_200_with_body(self):
        with patch("app.routers.books.book_repository.get") as mock_get:
            mock_get.return_value = VALID_BOOK.copy()
            response = client.get("/api/books/id1")

        assert response.status_code == 200
        assert response.json() == VALID_BOOK

    def test_get_book_not_found_returns_404(self):
        with patch("app.routers.books.book_repository.get") as mock_get:
            mock_get.return_value = None
            response = client.get("/api/books/nonexistent")

        assert response.status_code == 404
        assert "nonexistent" in response.json()["detail"]

    def test_get_book_dynamodb_client_error_returns_500(self):
        error_response = {"Error": {"Code": "InternalServerError", "Message": "Internal error"}}
        with patch("app.routers.books.book_repository.get") as mock_get:
            mock_get.side_effect = ClientError(error_response, "GetItem")
            response = client.get("/api/books/id1")

        assert response.status_code == 500

    def test_get_book_unexpected_error_returns_500(self):
        with patch("app.routers.books.book_repository.get") as mock_get:
            mock_get.side_effect = RuntimeError("unexpected")
            response = client.get("/api/books/id1")

        assert response.status_code == 500

    def test_get_book_passes_correct_id_to_repository(self):
        with patch("app.routers.books.book_repository.get") as mock_get:
            mock_get.return_value = VALID_BOOK.copy()
            client.get("/api/books/id42")

        mock_get.assert_called_once_with("id42")

    def test_get_book_response_schema_matches_spec(self):
        with patch("app.routers.books.book_repository.get") as mock_get:
            mock_get.return_value = VALID_BOOK.copy()
            response = client.get("/api/books/id1")

        body = response.json()
        for field in ("id", "author", "name", "note", "serial"):
            assert field in body, f"Field '{field}' missing from response"