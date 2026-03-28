import os
from unittest.mock import patch

# ---------------------------------------------------------------------------
# Fake AWS credentials — required by moto before any boto3 call
# ---------------------------------------------------------------------------
os.environ["AWS_DEFAULT_REGION"] = "ap-southeast-2"
os.environ["AWS_ACCESS_KEY_ID"] = "testing"
os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
os.environ["AWS_SECURITY_TOKEN"] = "testing"
os.environ["AWS_SESSION_TOKEN"] = "testing"

# ---------------------------------------------------------------------------
# Override Settings for all tests via env vars
# pydantic-settings reads these before .env so they take priority
# ---------------------------------------------------------------------------
os.environ["DYNAMODB_TABLE"] = "books-test"
os.environ["AWS_ACCOUNT_REGION"] = "ap-southeast-2"
os.environ["DYNAMODB_ENDPOINT_URL"] = ""  # no local endpoint

# ---------------------------------------------------------------------------
# Re-initialise the settings singleton so it picks up the overrides above
# ---------------------------------------------------------------------------
from app.settings import Settings
import app.settings as _settings_module
import app.repository as _repo_module

_settings_module.settings = Settings()
_repo_module.settings = _settings_module.settings