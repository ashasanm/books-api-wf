from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from app.routers import books

API_V1_PREFIX = "/api/v1"

app = FastAPI(
    title="Books API",
    description="RESTful API for managing books, deployed on AWS Lambda via Serverless Framework.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(books.router, prefix=API_V1_PREFIX)

# Lambda handler (Mangum adapts ASGI -> API Gateway)
handler = Mangum(app, lifespan="off")