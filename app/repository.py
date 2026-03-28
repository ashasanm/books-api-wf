import boto3
from botocore.exceptions import ClientError
from typing import Optional

from app.settings import settings


class BookRepository:
    """DynamoDB-backed repository for book records."""

    def __init__(self):
        kwargs = {"region_name": settings.aws_account_region}
        if settings.dynamodb_endpoint_url:
            kwargs["endpoint_url"] = settings.dynamodb_endpoint_url
        dynamodb = boto3.resource("dynamodb", **kwargs)
        self._table = dynamodb.Table(settings.dynamodb_table)

    def create(self, book_data: dict) -> None:
        """
        Persist a new book item.

        Raises:
            ValueError: if an item with the same id already exists.
            ClientError: on unexpected DynamoDB errors.
        """
        book_id = self._extract_id(book_data["id"])
        try:
            self._table.put_item(
                Item={**book_data, "bookId": book_id},
                ConditionExpression="attribute_not_exists(bookId)",
            )
        except ClientError as exc:
            if exc.response["Error"]["Code"] == "ConditionalCheckFailedException":
                raise ValueError(f"Book with id '{book_id}' already exists.")
            raise

    def get(self, book_id: str) -> Optional[dict]:
        """
        Retrieve a book by its bare id (e.g. "id1").

        Returns:
            The book dict, or None if not found.
        """
        response = self._table.get_item(Key={"bookId": book_id})
        item = response.get("Item")
        if item is None:
            return None
        item.pop("bookId", None)
        return item

    @staticmethod
    def _extract_id(resource_path: str) -> str:
        """Return the last path segment, e.g. '/books/id1' -> 'id1'."""
        return resource_path.rstrip("/").split("/")[-1]


# Module-level singleton used by routers
book_repository = BookRepository()