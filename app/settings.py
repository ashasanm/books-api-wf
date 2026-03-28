from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App
    stage: str = "dev"

    # DynamoDB
    dynamodb_table: str = "books-api-dev-books"
    dynamodb_endpoint_url: str | None = None

    # AWS
    aws_account_region: str = "ap-southeast-2"
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,

    )


settings = Settings()