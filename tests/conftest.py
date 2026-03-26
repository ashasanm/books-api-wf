import os
 
# Set env vars before any test module or app code is imported.
# This ensures moto and repository.py both see the correct values
# regardless of test execution order.
os.environ["DYNAMODB_TABLE"] = "books-integration"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
os.environ["AWS_ACCESS_KEY_ID"] = "testing"
os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
os.environ["AWS_SECURITY_TOKEN"] = "testing"
os.environ["AWS_SESSION_TOKEN"] = "testing"