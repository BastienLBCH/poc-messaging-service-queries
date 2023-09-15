import json

from fastapi import WebSocket

from app.middleware import validate_token
from app.database import interface


class ConnectionManager:
    def __init__(self):
        self.active_connections: list = []

    async def connect(self, websocket: WebSocket, token):
        payload = await validate_token(token)
        await websocket.accept()
        self.active_connections.append({'user': payload["sub"], 'websocket': websocket})
        print(self.active_connections)

    def disconnect(self, websocket: WebSocket):
        for connection in self.active_connections:
            if connection['websocket'] == websocket:
                self.active_connections.remove(connection)

    async def send_message(self, event: dict):
        conversation_id = event['conversation_id']
        users = interface.get_all_users_ids_from_conversation(conversation_id)
        for user in users:
            for connection in self.active_connections:
                if connection['user'] == user:
                    await connection['websocket'].send_text(json.dumps(event))

    async def create_conversation(self, event: dict):
        for connection in self.active_connections:
            if connection['user'] == event['creator_id']:
                await connection['websocket'].send_text(json.dumps(event))

    async def add_user_to_conversation(self, event: dict):
        for connection in self.active_connections:
            if connection['user'] == event['participant_id']:
                await connection['websocket'].send_text(json.dumps(event))

    async def remove_user_from_conversation(self, event: dict):
        for connection in self.active_connections:
            if connection['user'] == event['participant_id']:
                await connection['websocket'].send_text(json.dumps(event))

    async def delete_conversation(self, event: dict):
        conversation_id = event['conversation_id']
        users = interface.get_all_users_ids_from_conversation(conversation_id)
        for user in users:
            for connection in self.active_connections:
                if connection['user'] == user:
                    await connection['websocket'].send_text(json.dumps(event))

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)