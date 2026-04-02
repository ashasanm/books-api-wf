# Books API

A production-ready RESTful API built with **FastAPI**, deployed on **AWS Lambda** via **API Gateway**, backed by **AWS DynamoDB**, and managed end-to-end with the **Serverless Framework**.

---

## Table of Contents

1. [Architecture](#architecture)
2. [Project Structure](#project-structure)
3. [Git Setup](#git-setup)
4. [Prerequisites](#prerequisites)
5. [Local Development](#local-development)
6. [Running Tests](#running-tests)
7. [Deploying to AWS](#deploying-to-aws)
8. [API Reference](#api-reference)
9. [Web UI (Bonus)](#web-ui-bonus)

---

## Architecture

```
Browser / curl
     |
     v
AWS API Gateway  (HTTP API)
     |
     v
AWS Lambda  --- Mangum ASGI adapter ---> FastAPI app
     |
     v
AWS DynamoDB  (books table)
```

[Mangum](https://mangum.io/) bridges the API Gateway / Lambda event format to the standard ASGI interface that FastAPI uses.

### Application Layers

```
Request
  |
  v
Router      (app/routers/)      - HTTP wiring: paths, methods, status codes
  |
  v
Controller  (app/controllers/)  - HTTP error translation & logging
  |
  v
Service     (app/services/)     - Business logic
  |
  v
Repository  (app/repository.py) - DynamoDB data access
```

---

## Project Structure

```
books-api/
├── app/
│   ├── __init__.py
│   ├── main.py               # FastAPI app, CORS middleware & Mangum handler
│   ├── settings.py           # pydantic-settings config (reads from .env)
│   ├── schemas.py            # Pydantic request / response models
│   ├── repository.py         # DynamoDB data access layer (BookRepository)
│   ├── routers/
│   │   ├── __init__.py
│   │   └── books.py          # Route definitions only
│   ├── controllers/
│   │   ├── __init__.py
│   │   └── books.py          # HTTP error handling (BookController)
│   └── services/
│       ├── __init__.py
│       └── books.py          # Business logic (BookService)
├── tests/
│   ├── __init__.py
│   ├── conftest.py                  # Env var overrides & singleton reset
│   ├── test_books_unit.py           # Unit tests - router layer
│   ├── test_controller_unit.py      # Unit tests - controller layer
│   ├── test_service_unit.py         # Unit tests - service layer
│   ├── test_repository_unit.py      # Unit tests - repository layer
│   └── test_integration.py          # Integration tests - moto DynamoDB
├── web/
│   └── index.html            # Single-file browser UI (bonus)
├── .env.example              # Environment variable template
├── .gitignore
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
git commit -m "feat: initial project setup - FastAPI Books API"
```

### Recommended branching strategy

```
main          <- stable, production-ready
└── develop   <- integration branch
    ├── feat/add-delete-endpoint
    ├── fix/duplicate-book-error-message
    └── chore/update-dependencies
```

### Conventional commit messages

| Prefix | When to use |
|--------|-------------|
| `feat:` | New feature (endpoint, schema, etc.) |
| `fix:` | Bug fix |
| `test:` | Adding or updating tests |
| `chore:` | Dependency updates, config changes |
| `docs:` | README or docstring updates |
| `refactor:` | Code restructure, no behavior change |

---

## Prerequisites

| Tool | Version |
|------|---------|
| Python | >= 3.12 |
| Node.js | >= 22 (for Serverless Framework) |
| Serverless Framework | v4 |
| AWS CLI | configured with appropriate credentials |

```bash
npm install -g serverless@4
serverless login
```

> ### ⚠️ Windows Users — WSL Required for Deployment
>
> Running `serverless deploy` directly on Windows causes a
> `Runtime.ImportModuleError: No module named 'fastapi'` error on Lambda.
>
> This happens because Serverless packages Python dependencies using the
> Windows filesystem, producing a zip that is incompatible with the Linux
> Lambda runtime.
>
> **You must use [WSL (Windows Subsystem for Linux)](https://learn.microsoft.com/en-us/windows/wsl/install)
> and run all deployment commands from inside a WSL terminal.**
>
> ```bash
> # Step 1 — Install WSL (run once in PowerShell as Administrator)
> wsl --install
>
> # Step 2 — Open a WSL terminal, then run all commands from there
> cd /your/project/path
> source venv/bin/activate
> serverless deploy
> ```
>
> Running tests locally (`pytest`) does **not** require WSL — that works fine on Windows.

---

## Local Development

### 1. Create a virtual environment and install dependencies

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env
# Edit .env with your AWS credentials and table name
```

### 3. Run the API locally

```bash
uvicorn app.main:app --reload
```

The API is now available at `http://localhost:8000`.
Interactive docs: `http://localhost:8000/docs`

### 4. Quick smoke-test with curl

```bash
# Create a book
curl -s -X POST http://localhost:8000/api/v1/books \
  -H "Content-Type: application/json" \
  -d '{"id":"/books/id1","author":"/authors/id1","name":"Fancy Tech","note":"Great book","serial":"C040102"}' | python -m json.tool

# Retrieve the book
curl -s http://localhost:8000/api/v1/books/id1 | python -m json.tool
```

---

## Running Tests

All tests run **without any AWS credentials** - unit tests use `unittest.mock`
and the integration test uses [moto](https://docs.getmoto.org/) to emulate DynamoDB in-process.

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=app --cov-report=term-missing

# Run by layer
pytest tests/test_books_unit.py -v           # router
pytest tests/test_controller_unit.py -v      # controller
pytest tests/test_service_unit.py -v         # service
pytest tests/test_repository_unit.py -v      # repository
pytest tests/test_integration.py -v          # integration
```

Expected output (all tests passing):

```
tests/test_books_unit.py::TestCreateBook::test_create_book_duplicate_returns_400 PASSED
tests/test_books_unit.py::TestCreateBook::test_create_book_dynamodb_client_error_returns_500 PASSED
tests/test_books_unit.py::TestCreateBook::test_create_book_empty_body_returns_422 PASSED
tests/test_books_unit.py::TestCreateBook::test_create_book_extra_fields_ignored PASSED
tests/test_books_unit.py::TestCreateBook::test_create_book_missing_field_returns_422 PASSED
tests/test_books_unit.py::TestCreateBook::test_create_book_success_returns_201 PASSED
tests/test_books_unit.py::TestCreateBook::test_create_book_unexpected_error_returns_500 PASSED
tests/test_books_unit.py::TestGetBook::test_get_book_dynamodb_client_error_returns_500 PASSED
tests/test_books_unit.py::TestGetBook::test_get_book_not_found_returns_404 PASSED
tests/test_books_unit.py::TestGetBook::test_get_book_passes_correct_id_to_service PASSED
tests/test_books_unit.py::TestGetBook::test_get_book_response_schema_matches_spec PASSED
tests/test_books_unit.py::TestGetBook::test_get_book_success_returns_200_with_body PASSED
tests/test_books_unit.py::TestGetBook::test_get_book_unexpected_error_returns_500 PASSED
tests/test_controller_unit.py::TestBookControllerCreate::test_create_raises_400_on_duplicate PASSED
tests/test_controller_unit.py::TestBookControllerCreate::test_create_raises_500_on_client_error PASSED
tests/test_controller_unit.py::TestBookControllerCreate::test_create_raises_500_on_unexpected_error PASSED
tests/test_controller_unit.py::TestBookControllerCreate::test_create_succeeds_without_exception PASSED
tests/test_controller_unit.py::TestBookControllerGet::test_get_passes_correct_id_to_service PASSED
tests/test_controller_unit.py::TestBookControllerGet::test_get_raises_404_when_not_found PASSED
tests/test_controller_unit.py::TestBookControllerGet::test_get_raises_500_on_client_error PASSED
tests/test_controller_unit.py::TestBookControllerGet::test_get_raises_500_on_unexpected_error PASSED
tests/test_controller_unit.py::TestBookControllerGet::test_get_returns_book_dict PASSED
tests/test_service_unit.py::TestBookServiceCreate::test_create_delegates_to_repository PASSED
tests/test_service_unit.py::TestBookServiceCreate::test_create_propagates_client_error PASSED
tests/test_service_unit.py::TestBookServiceCreate::test_create_propagates_value_error_on_duplicate PASSED
tests/test_service_unit.py::TestBookServiceGet::test_get_propagates_client_error PASSED
tests/test_service_unit.py::TestBookServiceGet::test_get_returns_book_dict PASSED
tests/test_service_unit.py::TestBookServiceGet::test_get_returns_none_when_not_found PASSED
tests/test_repository_unit.py::TestExtractId::test_extracts_last_segment PASSED
tests/test_repository_unit.py::TestExtractId::test_handles_deep_path PASSED
tests/test_repository_unit.py::TestExtractId::test_handles_trailing_slash PASSED
tests/test_repository_unit.py::TestExtractId::test_single_segment PASSED
tests/test_repository_unit.py::TestCreate::test_create_calls_put_item PASSED
tests/test_repository_unit.py::TestCreate::test_create_raises_value_error_on_duplicate PASSED
tests/test_repository_unit.py::TestCreate::test_create_reraises_other_client_errors PASSED
tests/test_repository_unit.py::TestGet::test_get_passes_correct_key PASSED
tests/test_repository_unit.py::TestGet::test_get_returns_item_without_book_id_key PASSED
tests/test_repository_unit.py::TestGet::test_get_returns_none_when_not_found PASSED
tests/test_integration.py::TestBooksIntegration::test_create_duplicate_returns_400 PASSED
tests/test_integration.py::TestBooksIntegration::test_create_missing_fields_returns_422 PASSED
tests/test_integration.py::TestBooksIntegration::test_create_multiple_books_and_retrieve_each PASSED
tests/test_integration.py::TestBooksIntegration::test_create_then_get_book PASSED
tests/test_integration.py::TestBooksIntegration::test_get_nonexistent_book_returns_404 PASSED
```

---

## Deploying to AWS

> **Windows users:** run these commands inside WSL. See [Prerequisites](#prerequisites) for setup instructions.

### Deploy

```bash
source venv/bin/activate
serverless deploy
```

Serverless will output the API Gateway endpoint URL:

```
endpoints:
  POST - https://abc123.execute-api.ap-southeast-2.amazonaws.com/api/books
  GET  - https://abc123.execute-api.ap-southeast-2.amazonaws.com/api/books/{book_id}
```

### Deploy to a specific stage

```bash
serverless deploy --stage prod
```

### Tail live logs

```bash
serverless logs -f api -t
```

### Tear down

```bash
serverless remove
```

---

## API Reference

### POST `/api/books` - Create a book

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

### GET `/api/books/{id}` - Retrieve a book

**Path parameter:** `id` - the short book identifier (e.g. `id1`).

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
It lets you interact with the Books API directly from a browser — no Postman or curl needed.

### How to run

```bash
# 1. Start the API (in one terminal)
source venv/bin/activate
uvicorn app.main:app --reload

# 2. Serve the UI (in a second terminal)
cd web
python3 -m http.server 3000
```

Then open **`http://localhost:3000`** in any browser.

### Usage

1. Set the **API Base URL** at the top of the page:
   - Local development: `http://localhost:8000`
   - AWS deployed: `https://<api-id>.execute-api.ap-southeast-2.amazonaws.com`
2. Use the **Create a book** panel to fill in the fields and POST a new book.
3. Use the **Retrieve a book** panel to enter a book id and GET it.
4. The HTTP status code and response body are displayed inline after each request.

> **Note:** CORS is already enabled in `app/main.py` via `CORSMiddleware` so the browser UI can reach the API without any extra configuration.