"""
Integration test - spins up a local DynamoDB table via moto and exercises the
full request -> router -> repository -> DynamoDB stack.

Run with:
    pytest tests/test_integration.py -v
    pytest -v  (runs alongside unit tests)
"""

import pytest
import boto3
from moto import mock_aws
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture()
def client():
    """
    Single fixture that:
    1. Starts the moto mock (intercepts ALL boto3 calls for this test)
    2. Creates the DynamoDB table inside the mock context
    3. Yields a TestClient that runs in the same mock context
    4. Tears everything down automatically when the test ends
    """
    with mock_aws():
        dynamodb = boto3.resource("dynamodb", region_name="ap-southeast-2")
        dynamodb.create_table(
            TableName="books-integration",
            KeySchema=[{"AttributeName": "bookId", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "bookId", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )

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
        # ------- Create --------
        post_resp = client.post("/api/books", json=BOOK_PAYLOAD)
        assert post_resp.status_code == 201, post_resp.text

        # ------- Retrieve --------
        get_resp = client.get("/api/books/integ1")

        assert get_resp.status_code == 200
        body = get_resp.json()
        
        assert body["id"] == "/books/integ1"
        assert body["name"] == "Integration Testing 101"
        assert body["serial"] == "INT001"

    def test_get_nonexistent_book_returns_404(self, client):
        get_resp = client.get("/api/books/doesnotexist")
        assert get_resp.status_code == 404

    def test_create_duplicate_returns_400(self, client):
        client.post("/api/books", json=BOOK_PAYLOAD)
        second = client.post("/api/books", json=BOOK_PAYLOAD)
        assert second.status_code == 400
        assert "already exists" in second.json()["detail"]

    def test_create_missing_fields_returns_422(self, client):
        incomplete = {"id": "/books/x", "author": "/authors/x"}
        resp = client.post("/api/books", json=incomplete)
        assert resp.status_code == 422

    def test_create_multiple_books_and_retrieve_each(self, client):
        books = [
            {**BOOK_PAYLOAD, "id": f"/books/b{i}", "serial": f"S{i:03d}"}
            for i in range(1, 4)
        ]
        for book in books:
            assert client.post("/api/books", json=book).status_code == 201

        for book in books:
            book_id = book["id"].split("/")[-1]
            resp = client.get(f"/api/books/{book_id}")
            assert resp.status_code == 200
            assert resp.json()["serial"] == book["serial"]