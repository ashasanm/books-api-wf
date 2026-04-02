"""
Integration test - exercises the full stack:
Router -> Controller -> Service -> Repository -> DynamoDB (moto)

Run with:
    pytest tests/test_integration.py -v
    pytest -v  (runs alongside unit tests)
"""

import pytest
import boto3
from unittest.mock import patch
from moto import mock_aws
from fastapi.testclient import TestClient

from app.main import app
from app.settings import settings
from app.repository import BookRepository


@pytest.fixture()
def client():
    """
    Start moto, create the DynamoDB table, inject a real BookRepository
    pointing at the moto-backed table into the service layer.

    Flow: TestClient -> Router -> Controller -> Service -> moto DynamoDB
    """
    with mock_aws():
        dynamodb = boto3.resource("dynamodb", region_name=settings.aws_account_region)
        table = dynamodb.create_table(
            TableName=settings.dynamodb_table,
            KeySchema=[{"AttributeName": "bookId", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "bookId", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )

        # Bypass __init__ to avoid a real boto3 connection,
        # then inject the moto table directly
        repo = BookRepository.__new__(BookRepository)
        repo._table = table

        # Patch at the service layer — where book_repository is actually used
        with patch("app.services.books.book_repository", repo):
            with TestClient(app) as c:
                yield c


BOOK_PAYLOAD = {
    "id": "/books/integ1",
    "author": "/authors/a1",
    "name": "Integration Testing 101",
    "note": "A hands-on guide to integration tests.",
    "serial": "INT001",
}


class TestBooksIntegration:
    def test_create_then_get_book(self, client):
        """Full round-trip: create a book, then retrieve it."""
        post_resp = client.post("/api/v1/books", json=BOOK_PAYLOAD)
        assert post_resp.status_code == 201, post_resp.text

        get_resp = client.get("/api/v1/books/integ1")
        assert get_resp.status_code == 200
        body = get_resp.json()
        assert body["id"] == "/books/integ1"
        assert body["name"] == "Integration Testing 101"
        assert body["serial"] == "INT001"

    def test_get_nonexistent_book_returns_404(self, client):
        get_resp = client.get("/api/v1/books/doesnotexist")
        assert get_resp.status_code == 404

    def test_create_duplicate_returns_400(self, client):
        client.post("/api/v1/books", json=BOOK_PAYLOAD)
        second = client.post("/api/v1/books", json=BOOK_PAYLOAD)
        assert second.status_code == 400
        assert "already exists" in second.json()["detail"]

    def test_create_missing_fields_returns_422(self, client):
        incomplete = {"id": "/books/x", "author": "/authors/x"}
        resp = client.post("/api/v1/books", json=incomplete)
        assert resp.status_code == 422

    def test_create_multiple_books_and_retrieve_each(self, client):
        books = [
            {**BOOK_PAYLOAD, "id": f"/books/b{i}", "serial": f"S{i:03d}"}
            for i in range(1, 4)
        ]
        for book in books:
            assert client.post("/api/v1/books", json=book).status_code == 201

        for book in books:
            book_id = book["id"].split("/")[-1]
            resp = client.get(f"/api/v1/books/{book_id}")
            assert resp.status_code == 200
            assert resp.json()["serial"] == book["serial"]