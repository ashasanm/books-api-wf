from fastapi import FastAPI
from mangum import Mangum
from app.routers import books

app = FastAPI(
    title="Books API",
    description="RESTful API for managing books, deployed on AWS Lambda via Serverless Framework.",
    version="1.0.0",
)

app.include_router(books.router, prefix="/api")

# Lambda handler (Mangum adapts ASGI → API Gateway)
handler = Mangum(app, lifespan="off")
