"""
Unit tests for app/repository.py — BookRepository class.
All boto3 calls are mocked via unittest.mock.
"""

import pytest
from unittest.mock import patch, MagicMock
from botocore.exceptions import ClientError

from app.repository import BookRepository


@pytest.fixture()
def repo():
    """Return a BookRepository with a mocked DynamoDB table."""
    with patch("app.repository.boto3.resource") as mock_resource:
        mock_table = MagicMock()
        mock_resource.return_value.Table.return_value = mock_table
        repository = BookRepository()
        repository._table = mock_table
        yield repository, mock_table


# ---------------------------------------------------------------------------
# _extract_id helper
# ---------------------------------------------------------------------------


class TestExtractId:
    def test_extracts_last_segment(self):
        assert BookRepository._extract_id("/books/id1") == "id1"

    def test_handles_trailing_slash(self):
        assert BookRepository._extract_id("/books/id1/") == "id1"

    def test_handles_deep_path(self):
        assert BookRepository._extract_id("/a/b/c/d") == "d"

    def test_single_segment(self):
        assert BookRepository._extract_id("id1") == "id1"


# ---------------------------------------------------------------------------
# BookRepository.create
# ---------------------------------------------------------------------------


class TestCreate:
    def test_create_calls_put_item(self, repo):
        repository, mock_table = repo
        repository.create({
            "id": "/books/id1",
            "author": "/authors/id1",
            "name": "Fancy Tech",
            "note": "Great",
            "serial": "C001",
        })

        mock_table.put_item.assert_called_once()
        call_kwargs = mock_table.put_item.call_args.kwargs
        assert call_kwargs["Item"]["bookId"] == "id1"

    def test_create_raises_value_error_on_duplicate(self, repo):
        repository, mock_table = repo
        error_response = {"Error": {"Code": "ConditionalCheckFailedException", "Message": ""}}
        mock_table.put_item.side_effect = ClientError(error_response, "PutItem")

        with pytest.raises(ValueError, match="already exists"):
            repository.create({
                "id": "/books/id1", "author": "/authors/id1",
                "name": "X", "note": "Y", "serial": "Z"
            })

    def test_create_reraises_other_client_errors(self, repo):
        repository, mock_table = repo
        error_response = {"Error": {"Code": "ProvisionedThroughputExceededException", "Message": ""}}
        mock_table.put_item.side_effect = ClientError(error_response, "PutItem")

        with pytest.raises(ClientError):
            repository.create({
                "id": "/books/id1", "author": "/authors/id1",
                "name": "X", "note": "Y", "serial": "Z"
            })


# ---------------------------------------------------------------------------
# BookRepository.get
# ---------------------------------------------------------------------------


class TestGet:
    def test_get_returns_item_without_book_id_key(self, repo):
        repository, mock_table = repo
        mock_table.get_item.return_value = {
            "Item": {
                "bookId": "id1",
                "id": "/books/id1",
                "author": "/authors/id1",
                "name": "Fancy Tech",
                "note": "Great",
                "serial": "C001",
            }
        }

        result = repository.get("id1")

        assert result is not None
        assert "bookId" not in result
        assert result["id"] == "/books/id1"

    def test_get_returns_none_when_not_found(self, repo):
        repository, mock_table = repo
        mock_table.get_item.return_value = {}

        result = repository.get("missing")

        assert result is None

    def test_get_passes_correct_key(self, repo):
        repository, mock_table = repo
        mock_table.get_item.return_value = {}

        repository.get("id99")

        mock_table.get_item.assert_called_once_with(Key={"bookId": "id99"})