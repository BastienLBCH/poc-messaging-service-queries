import asyncio
import random
import string
import uuid
import requests

from app.database import schemas, models
from app.database.database import SessionLocal, engine
from app.main import handle_event
from app.settings import Settings
from app import utils

db = SessionLocal()


def login_user(username: str, password: str, settings: Settings):
    """
    Return access token and user_id for specific user
    :param username:
    :param password:
    :return:
    """
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = f"client_id={settings.keycloak_client_id}&username={username}&password={password}&grant_type=password"
    r = requests.post(headers=headers, data=data, url=settings.keycloak_token_url)
    access_token = r.json()["access_token"]
    user_id = utils.get_userid_from_token(access_token)
    return user_id, access_token


class TestMessages:
    def setup_method(self):
        models.Base.metadata.create_all(bind=engine)
        self.db = db

        settings = Settings()

        self.user_id, self.access_token = login_user(settings.keycloak_username_test, settings.keycloak_password_test, settings)
        self.user_id_2, self.access_token_2 = login_user(settings.keycloak_username_test_2, settings.keycloak_password_test, settings)

        # Prepare conversation for further tests
        id_conversation = str(uuid.uuid4())
        self.created_conversation = {
            "id": id_conversation,
            "name": "conversation test",
            "creator_id": self.user_id,
            "event": "userCreatedConversation",
            "created_at": "2023-08-28T07:23:31.353437Z"
        }
        asyncio.run(handle_event(self.created_conversation))

    def test_user_sent_message(self):
        id_conversation = self.created_conversation['id']
        message_content = ''.join(random.choice(string.ascii_letters) for i in range(25))
        event = {
            "id": 1,
            "user_id": self.user_id,
            "conversation_id": id_conversation,
            "message_content": message_content,
            "event": "userSentMessageToConversation",
            "created_at": "2023-08-29T08:55:26.694214Z"
        }
        asyncio.run(handle_event(event))

        db_conversation = db.query(models.Conversation) \
            .filter(models.Conversation.id == id_conversation) \
            .first()

        message_is_in_conversation = False
        for message in db_conversation.messages:
            if message.content == message_content:
                message_is_in_conversation = True

        assert message_is_in_conversation is True

    def test_user_not_in_conversation_cant_send_message(self):
        """
        Test that a user who's not in a conversation can't send message
        :return:
        """
        id_conversation = self.created_conversation['id']
        message_content = ''.join(random.choice(string.ascii_letters) for i in range(25))
        event = {
            "id": 1,
            "user_id": self.user_id_2,
            "conversation_id": id_conversation,
            "message_content": message_content,
            "event": "userSentMessageToConversation",
            "created_at": "2023-08-29T08:55:26.694214Z"
        }
        asyncio.run(handle_event(event))

        db_conversation = db.query(models.Conversation) \
            .filter(models.Conversation.id == id_conversation) \
            .first()

        message_is_in_conversation = False
        for message in db_conversation.messages:
            if message.content == message_content:
                message_is_in_conversation = True

        assert message_is_in_conversation is False
