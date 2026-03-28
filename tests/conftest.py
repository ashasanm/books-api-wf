import os

# ---------------------------------------------------------------------------
# Fake AWS credentials — required by moto before any boto3 call
# ---------------------------------------------------------------------------
os.environ["AWS_DEFAULT_REGION"] = "ap-southeast-1"
os.environ["AWS_ACCESS_KEY_ID"] = "testing"
os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
os.environ["AWS_SECURITY_TOKEN"] = "testing"
os.environ["AWS_SESSION_TOKEN"] = "testing"

# ---------------------------------------------------------------------------
# Override settings for all tests
# pydantic-settings reads env vars before .env so these take priority
# ---------------------------------------------------------------------------
os.environ["DYNAMODB_TABLE"] = "books-test"
os.environ["AWS_ACCOUNT_REGION"] = "ap-southeast-1"
os.environ["DYNAMODB_ENDPOINT_URL"] = ""

# ---------------------------------------------------------------------------
# Re-initialise singletons so they pick up the overrides above
# ---------------------------------------------------------------------------
from app.settings import Settings
import app.settings as _settings_module
import app.repository as _repo_module

_settings_module.settings = Settings()
_repo_module.settings = _settings_module.settings
_repo_module.book_repository = _repo_module.BookRepository()