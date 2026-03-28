# Books API

A production-ready RESTful API built with **FastAPI**, deployed on **AWS Lambda** via **API Gateway**, backed by **AWS DynamoDB**, and managed end-to-end with the **Serverless Framework**.

---

## Table of Contents

1. [Architecture](#architecture)
2. [Project Structure](#project-structure)
3. [Git Setup](#git-setup)
4. [Prerequisites](#prerequisites)
4. [Local Development](#local-development)
5. [Running Tests](#running-tests)
6. [Deploying to AWS](#deploying-to-aws)
7. [API Reference](#api-reference)
8. [Web UI (Bonus)](#web-ui-bonus)

---

## Architecture

```
Browser / curl
     │
     ▼
AWS API Gateway  (HTTP API)
     │
     ▼
AWS Lambda  ─── Mangum ASGI adapter ──► FastAPI app
     │
     ▼
AWS DynamoDB  (books table)
```

[Mangum](https://mangum.io/) bridges the API Gateway / Lambda event format to the standard ASGI interface that FastAPI uses.

---

## Project Structure

```
books-api/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application & Mangum handler
│   ├── schemas.py       # Pydantic request / response models
│   ├── repository.py    # DynamoDB data access layer
│   └── routers/
│       ├── __init__.py
│       └── books.py     # POST /api/books  &  GET /api/books/{id}
├── tests/
│   ├── __init__.py
│   ├── test_books_unit.py       # Unit tests – router (all mocked)
│   ├── test_repository_unit.py  # Unit tests – repository layer
│   └── test_integration.py      # Integration test – moto DynamoDB
├── web/
│   └── index.html       # Single-file browser UI (bonus)
├── requirements.txt
├── serverless.yml
├── pytest.ini
└── README.md
```

---

## Git Setup

### Initial setup

```bash
git init
git add .
git commit -m "feat: initial project setup – FastAPI Books API"
```

### Recommended branching strategy

```
main          ← stable, production-ready
└── develop   ← integration branch
    ├── feat/add-delete-endpoint
    ├── fix/duplicate-book-error-message
    └── chore/update-dependencies
```

### Conventional commit messages used in this project

| Prefix | When to use |
|--------|-------------|
| `feat:` | New feature (endpoint, schema, etc.) |
| `fix:` | Bug fix |
| `test:` | Adding or updating tests |
| `chore:` | Dependency updates, config changes |
| `docs:` | README or docstring updates |
| `refactor:` | Code restructure, no behavior change |

### Example commit history

```bash
git commit -m "feat: add POST /api/books endpoint"
git commit -m "feat: add GET /api/books/{id} endpoint"
git commit -m "feat: add DynamoDB repository layer"
git commit -m "test: add unit tests for books router"
git commit -m "test: add integration tests with moto"
git commit -m "chore: add serverless.yml for AWS deployment"
git commit -m "docs: update README with setup and deploy instructions"
```

---

## Prerequisites

| Tool | Version |
|------|---------|
| Python | ≥ 3.12 |
| Node.js | ≥ 18 (for Serverless Framework) |
| Serverless Framework | v4 | https://serverless.com
| AWS CLI | configured with appropriate credentials | https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html

Install Serverless Framework and the Python plugin:

```bash
npm install -g serverless@4
```

> Serverless Framework v4 requires a free account. Log in with:
> ```bash
> serverless login
> ```

---

## Local Development

### 1. Create a virtual environment and install dependencies

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run the API locally (with Uvicorn)

```bash
python -m uvicorn app.main:app --reload
```

The API is now available at `http://localhost:8000`.  
Interactive docs: `http://localhost:8000/docs`

> **Note:** Running locally uses real AWS credentials and the DynamoDB table
> specified by the `DYNAMODB_TABLE` environment variable (default: `books`).
> Either create the table in AWS first or point to a local DynamoDB instance:
>
> ```bash
> DYNAMODB_ENDPOINT_URL=http://localhost:8001 uvicorn app.main:app --reload
> ```

### 3. Quick smoke-test with curl

```bash
# Create a book
curl -s -X POST http://localhost:8000/api/books \
  -H "Content-Type: application/json" \
  -d '{"id":"/books/id1","author":"/authors/id1","name":"Fancy Tech","note":"Great book","serial":"C040102"}' | python -m json.tool

# Retrieve the book
curl -s http://localhost:8000/api/books/id1 | python -m json.tool
```

---

## Running Tests

All tests run **without any AWS credentials** – unit tests use `unittest.mock`
and the integration test uses [moto](https://docs.getmoto.org/) to emulate DynamoDB in-process.

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=app --cov-report=term-missing

# Run only unit tests
pytest tests/test_books_unit.py tests/test_repository_unit.py -v

# Run only the integration test
pytest tests/test_integration.py -v
```

Expected output (all tests passing):

```
tests/test_books_unit.py::TestCreateBook::test_create_book_calls_repository_with_correct_data PASSED
tests/test_books_unit.py::TestCreateBook::test_create_book_duplicate_returns_400 PASSED
tests/test_books_unit.py::TestCreateBook::test_create_book_dynamodb_client_error_returns_500 PASSED
tests/test_books_unit.py::TestCreateBook::test_create_book_empty_body_returns_422 PASSED
tests/test_books_unit.py::TestCreateBook::test_create_book_extra_fields_ignored PASSED
tests/test_books_unit.py::TestCreateBook::test_create_book_missing_field_returns_400 PASSED
tests/test_books_unit.py::TestCreateBook::test_create_book_success_returns_201 PASSED
tests/test_books_unit.py::TestCreateBook::test_create_book_unexpected_error_returns_500 PASSED
tests/test_books_unit.py::TestGetBook::test_get_book_dynamodb_client_error_returns_500 PASSED
tests/test_books_unit.py::TestGetBook::test_get_book_not_found_returns_404 PASSED
tests/test_books_unit.py::TestGetBook::test_get_book_passes_correct_id_to_repository PASSED
tests/test_books_unit.py::TestGetBook::test_get_book_response_schema_matches_spec PASSED
tests/test_books_unit.py::TestGetBook::test_get_book_success_returns_200_with_body PASSED
tests/test_books_unit.py::TestGetBook::test_get_book_unexpected_error_returns_500 PASSED
tests/test_repository_unit.py::TestExtractId::... PASSED (×4)
tests/test_repository_unit.py::TestCreateBook::... PASSED (×3)
tests/test_repository_unit.py::TestGetBook::... PASSED (×3)
tests/test_integration.py::TestBooksIntegration::test_create_duplicate_returns_400 PASSED
tests/test_integration.py::TestBooksIntegration::test_create_missing_fields_returns_422 PASSED
tests/test_integration.py::TestBooksIntegration::test_create_multiple_books_and_retrieve_each PASSED
tests/test_integration.py::TestBooksIntegration::test_create_then_get_book PASSED
tests/test_integration.py::TestBooksIntegration::test_get_nonexistent_book_returns_404 PASSED
```

---

## Deploying to AWS

### 1. Configure AWS credentials

```bash
aws configure   # or set AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY env vars
```

### 2. Deploy

```bash
# Deploy to the default dev stage in us-east-1
serverless deploy

# Deploy to production
serverless deploy --stage prod --region eu-west-1
```

Serverless will output the API Gateway endpoint URL, e.g.:

```
endpoints:
  POST - https://abc123xyz.execute-api.us-east-1.amazonaws.com/api/books
  GET  - https://abc123xyz.execute-api.us-east-1.amazonaws.com/api/books/{book_id}
```

### 3. Tear down

```bash
serverless remove
```

---

## API Reference

### POST `/api/books` — Create a book

**Request body** (`application/json`):

```json
{
  "id":     "/books/id1",
  "author": "/authors/id1",
  "name":   "Fancy Tech",
  "note":   "Awesome book for beginners in Fancy.",
  "serial": "C040102"
}
```

| Status | Condition |
|--------|-----------|
| `201 Created` | Book stored successfully |
| `400 Bad Request` | Duplicate book id |
| `422 Unprocessable Entity` | Missing / invalid fields |
| `500 Internal Server Error` | Unexpected server error |

---

### GET `/api/books/{id}` — Retrieve a book

**Path parameter:** `id` — the short book identifier (e.g. `id1`).

**Example:** `GET /api/books/id1`

**Success response** (`200 OK`):

```json
{
  "id":     "/books/id1",
  "author": "/authors/id1",
  "name":   "Fancy Tech",
  "note":   "Awesome book for beginners in Fancy.",
  "serial": "C040102"
}
```

| Status | Condition |
|--------|-----------|
| `200 OK` | Book found |
| `404 Not Found` | No book with the given id |
| `500 Internal Server Error` | Unexpected server error |

---

## Web UI (Bonus)

A zero-dependency, single-file browser UI is included at `web/index.html`.

**To use it:**

1. Open `web/index.html` in any browser (double-click or `open web/index.html`).
2. Set the **API Base URL** to your running API (local or AWS endpoint).
3. Use the **Create a book** form to POST a new book.
4. Use the **Retrieve a book** form to GET a book by id.

The UI works directly against the live API — no build step, no server required.  
It fulfils the bonus requirement of accessing the API from a web application running in a browser.

> If you run the API locally and open the HTML file from disk, ensure CORS
> is enabled. FastAPI does not add CORS headers by default; add
> `CORSMiddleware` to `app/main.py` for local development:
>
> ```python
> from fastapi.middleware.cors import CORSMiddleware
> app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
> ```
