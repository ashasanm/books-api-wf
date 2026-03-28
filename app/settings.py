from typing import List, Union
from pydantic import Field, field_validator 
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App
    stage: str = "dev"
    allowed_origins: Union[str, List[str]] = Field(alias="ALLOWED_ORIGINS")

    # DynamoDB
    dynamodb_table: str = "books-api-dev-books"
    dynamodb_endpoint_url: str | None = None

    # AWS
    aws_account_region: str = "ap-southeast-2"
    aws_access_key_id: str | None = Field(alias="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: str | None = Field(alias="AWS_SECRET_ACCESS_KEY")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,

    )

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_origins(cls, v: Union[str, List[str]]) -> List[str]:
        # Handle the case where AWS sends a string (like from your .env)
        if isinstance(v, str):
            return [item.strip() for item in v.split(",") if item.strip()]
        
        # Handle the case where AWS sends a list (which caused your error)
        if isinstance(v, list):
            return v
            
        return v


settings = Settings()