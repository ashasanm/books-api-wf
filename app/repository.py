import boto3
from botocore.exceptions import ClientError
from typing import Optional

from app.settings import settings


def _get_table():
    """Return a DynamoDB Table resource, honouring local endpoint override."""
    kwargs = {"region_name": settings.aws_account_region}
    if settings.dynamodb_endpoint_url:
        kwargs["endpoint_url"] = settings.dynamodb_endpoint_url
    dynamodb = boto3.resource("dynamodb", **kwargs)
    return dynamodb.Table(settings.dynamodb_table)


def create_book(book_data: dict) -> None:
    """
    Persist a new book item.

    Raises:
        ValueError: if an item with the same id already exists.
        ClientError: on unexpected DynamoDB errors.
    """
    table = _get_table()
    book_id = _extract_id(book_data["id"])
    try:
        table.put_item(
            Item={**book_data, "bookId": book_id},
            ConditionExpression="attribute_not_exists(bookId)",
        )
    except ClientError as exc:
        if exc.response["Error"]["Code"] == "ConditionalCheckFailedException":
            raise ValueError(f"Book with id '{book_id}' already exists.")
        raise


def get_book(book_id: str) -> Optional[dict]:
    """
    Retrieve a book by its bare id (e.g. "id1").

    Returns:
        The book dict, or None if not found.
    """
    table = _get_table()
    response = table.get_item(Key={"bookId": book_id})
    item = response.get("Item")
    if item is None:
        return None
    item.pop("bookId", None)
    return item


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_id(resource_path: str) -> str:
    """Return the last path segment, e.g. '/books/id1' -> 'id1'."""
    return resource_path.rstrip("/").split("/")[-1]