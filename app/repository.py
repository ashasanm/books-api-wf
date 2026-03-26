import os
import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from typing import Optional

TABLE_NAME = os.environ.get("DYNAMODB_TABLE", "books")
AWS_REGION = os.environ.get("AWS_ACCOUNT_REGION", os.environ.get("AWS_REGION", "us-east-1"))


def _get_table():
    """Return a DynamoDB Table resource, honouring local endpoint override."""
    endpoint_url = os.environ.get("DYNAMODB_ENDPOINT_URL")  # for local testing
    kwargs = {"region_name": AWS_REGION}
    if endpoint_url:
        kwargs["endpoint_url"] = endpoint_url
    dynamodb = boto3.resource("dynamodb", **kwargs)
    return dynamodb.Table(TABLE_NAME)


def create_book(book_data: dict) -> None:
    """
    Persist a new book item.

    Raises:
        ValueError: if an item with the same id already exists.
        ClientError: on unexpected DynamoDB errors.
    """
    table = _get_table()
    # Extract the bare id key (e.g. "id1") used as the DynamoDB partition key
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
    # Remove the internal partition-key attribute before returning
    item.pop("bookId", None)
    return item


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_id(resource_path: str) -> str:
    """Return the last path segment, e.g. '/books/id1' → 'id1'."""
    return resource_path.rstrip("/").split("/")[-1]
