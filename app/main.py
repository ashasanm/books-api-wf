from fastapi import FastAPI
from mangum import Mangum
from app.routers import books
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Books API",
    description="RESTful API for managing books, deployed on AWS Lambda via Serverless Framework.",
    version="1.0.0",
)

app.include_router(books.router, prefix="/api")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)  # this should be changed to predefined web app url, and allowed headers

# Lambda handler (Mangum adapts ASGI → API Gateway)
handler = Mangum(app, lifespan="off")
