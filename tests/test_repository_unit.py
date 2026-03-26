"""
Unit tests for app/repository.py.

All boto3 calls are mocked via moto (or unittest.mock) so no real AWS
resources are required.
"""

import pytest
from unittest.mock import patch, MagicMock
from botocore.exceptions import ClientError

from app import repository


# ---------------------------------------------------------------------------
# _extract_id helper
# ---------------------------------------------------------------------------


class TestExtractId:
    def test_extracts_last_segment(self):
        assert repository._extract_id("/books/id1") == "id1"

    def test_handles_trailing_slash(self):
        assert repository._extract_id("/books/id1/") == "id1"

    def test_handles_deep_path(self):
        assert repository._extract_id("/a/b/c/d") == "d"

    def test_single_segment(self):
        assert repository._extract_id("id1") == "id1"


# ---------------------------------------------------------------------------
# create_book
# ---------------------------------------------------------------------------


class TestCreateBook:
    def _make_table_mock(self):
        table = MagicMock()
        return table

    def test_create_book_calls_put_item(self):
        table_mock = self._make_table_mock()
        with patch("app.repository._get_table", return_value=table_mock):
            repository.create_book(
                {
                    "id": "/books/id1",
                    "author": "/authors/id1",
                    "name": "Fancy Tech",
                    "note": "Great",
                    "serial": "C001",
                }
            )

        table_mock.put_item.assert_called_once()
        call_kwargs = table_mock.put_item.call_args.kwargs
        assert call_kwargs["Item"]["bookId"] == "id1"

    def test_create_book_raises_value_error_on_duplicate(self):
        table_mock = self._make_table_mock()
        error_response = {
            "Error": {"Code": "ConditionalCheckFailedException", "Message": ""}
        }
        table_mock.put_item.side_effect = ClientError(error_response, "PutItem")

        with patch("app.repository._get_table", return_value=table_mock):
            with pytest.raises(ValueError, match="already exists"):
                repository.create_book(
                    {"id": "/books/id1", "author": "/authors/id1", "name": "X", "note": "Y", "serial": "Z"}
                )

    def test_create_book_re_raises_other_client_errors(self):
        table_mock = self._make_table_mock()
        error_response = {"Error": {"Code": "ProvisionedThroughputExceededException", "Message": ""}}
        table_mock.put_item.side_effect = ClientError(error_response, "PutItem")

        with patch("app.repository._get_table", return_value=table_mock):
            with pytest.raises(ClientError):
                repository.create_book(
                    {"id": "/books/id1", "author": "/authors/id1", "name": "X", "note": "Y", "serial": "Z"}
                )


# ---------------------------------------------------------------------------
# get_book
# ---------------------------------------------------------------------------


class TestGetBook:
    def test_get_book_returns_item_without_book_id_key(self):
        table_mock = MagicMock()
        table_mock.get_item.return_value = {
            "Item": {
                "bookId": "id1",
                "id": "/books/id1",
                "author": "/authors/id1",
                "name": "Fancy Tech",
                "note": "Great",
                "serial": "C001",
            }
        }

        with patch("app.repository._get_table", return_value=table_mock):
            result = repository.get_book("id1")

        assert result is not None
        assert "bookId" not in result
        assert result["id"] == "/books/id1"

    def test_get_book_returns_none_when_not_found(self):
        table_mock = MagicMock()
        table_mock.get_item.return_value = {}  # no 'Item' key

        with patch("app.repository._get_table", return_value=table_mock):
            result = repository.get_book("missing")

        assert result is None

    def test_get_book_passes_correct_key(self):
        table_mock = MagicMock()
        table_mock.get_item.return_value = {}

        with patch("app.repository._get_table", return_value=table_mock):
            repository.get_book("id99")

        table_mock.get_item.assert_called_once_with(Key={"bookId": "id99"})
