import threading
import asyncio
import os

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
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.kafka_client import kafka_worker
from app.middleware import ValidatingMiddleware
from app.database import models, schemas
from app.database.interface import (
    get_all_conversations_from_user,
    get_all_messages_from_conversation,
    create_conversation,
    add_user_to_conversation,
    add_message_to_conversation,
    remove_user_from_conversation,
    delete_conversation,
    get_all_users_from_conversation,
)
from app.database.database import engine, SessionLocal
from app.utils import get_userid_from_request
from app.settings import Settings
from app.websockets import ConnectionManager

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")

connection_manager = ConnectionManager()


async def handle_event(event):
    if event['event'] == "userCreatedConversation":
        if create_conversation(event):
            await connection_manager.create_conversation(event)
    elif event['event'] == "userAddedParticipantToConversation":
        if add_user_to_conversation(event):
            await connection_manager.add_user_to_conversation(event)
    elif event['event'] == "userSentMessageToConversation":
        if add_message_to_conversation(event):
            await connection_manager.send_message(event)
    elif event['event'] == "userRemovedParticipantToConversation":
        if remove_user_from_conversation(event):
            await connection_manager.remove_user_from_conversation(event)
    elif event['event'] == "userDeletedConversation":
        if delete_conversation(event):
            await connection_manager.delete_conversation(event)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@asynccontextmanager
async def lifespan(app: FastAPI):
    # Poll for new messages from Kafka and print them.
    stop_threads = False
    mythread = threading.Thread(target=kafka_worker, args=(handle_event, lambda: stop_threads, ))
    mythread.start()
    yield
    stop_threads = True
    mythread.join()


settings = Settings()

app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")

authmiddleware = ValidatingMiddleware()
app.add_middleware(BaseHTTPMiddleware, dispatch=authmiddleware)


@app.websocket("/ws/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str):
    try:
        await connection_manager.connect(websocket, token)
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)
    except Exception as e:
        print(f"\n###\n Websocket exception: {e} \n###\n")


@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            'keycloak_token_url': settings.keycloak_token_url,
            'keycloak_users_url': settings.keycloak_users_url,
            'keycloak_client_id': settings.keycloak_client_id,
            'command_server': settings.command_server,
            'access_url': settings.access_url
        })


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


@app.get("/conversations/{conversation_id}/members", response_model=list[schemas.User])
def get_conversation_members(request: Request, conversation_id: str):
    """
    Return all users from a conversation
    :param request:
    :param conversation_id: str id of the conversation to get
    :return:
    """
    try:
        user_id = get_userid_from_request(request)
        users = get_all_users_from_conversation(user_id, conversation_id)
        if users is None:
            raise Exception()
        return users
    except Exception as e:
        raise HTTPException(status_code=400, detail='Something went wrong')


@app.get("/decodetoken")
def returnDecodedJWT(request: Request):
    return get_userid_from_request(request)

