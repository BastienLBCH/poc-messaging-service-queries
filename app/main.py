from multiprocessing import Process

from contextlib import asynccontextmanager
from fastapi import (
    FastAPI,
    Request,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
    WebSocketException
)
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.templating import Jinja2Templates

from app.kafka_client import kafka_worker
from app.middleware import ValidatingMiddleware
from app.database import models, schemas
from app.database.interface import get_all_conversations_from_user, \
    get_all_messages_from_conversation
from app.database.database import engine, SessionLocal
from app.utils import get_userid_from_request
from app.websockets import ConnectionManager

models.Base.metadata.create_all(bind=engine)

connection_manager = ConnectionManager()
templates = Jinja2Templates(directory="templates")


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


@app.websocket("/ws/{token}")
async def websocket_endpoint(websocket: WebSocket, token: int):
    try:
        await connection_manager.connect(websocket, token)
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)
    except Exception:
        pass


@app.get("/ping")
def test():
    return {"message": "pong"}


@app.get("/conversations", response_model=list[schemas.Conversation])
def get_user_conversations(request: Request):
    """
    Return all conversations from user
    :param request:
    :return:
    """
    try:
        user_id = get_userid_from_request(request)
        return get_all_conversations_from_user(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="something went wrong")



@app.get("/conversations/{conversation_id}", response_model=list[schemas.Message])
def get_messages_from_conversations(request: Request, conversation_id: str):
    """
    Return all message from a conversation
    :param request:
    :return:
    """
    try:
        user_id = get_userid_from_request(request)
        messages = get_all_messages_from_conversation(user_id, conversation_id)
        if messages is None:
            raise Exception()
        return messages
    except Exception:
        raise HTTPException(status_code=400, detail='Something went wrong')




