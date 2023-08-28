from multiprocessing import Process

from contextlib import asynccontextmanager
from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware

from app.kafka_client import kafka_worker
from app.middleware import ValidatingMiddleware
from app.database import models
from app.database.database import engine, SessionLocal

models.Base.metadata.create_all(bind=engine)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Poll for new messages from Kafka and print them.
    process = Process(target=kafka_worker, args=())
    process.start()
    yield
    process.terminate()


app = FastAPI(lifespan=lifespan)

authmiddleware = ValidatingMiddleware()
app.add_middleware(BaseHTTPMiddleware, dispatch=authmiddleware)


@app.get("/ping")
def test():
    return {"message": "pong"}



