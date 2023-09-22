import asyncio
import uuid
import requests

from app.database import models
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


class TestCreateConversation:
    def setup_method(self):
        """
        Initiate database for creating conversation test
        :return:
        """
        models.Base.metadata.create_all(bind=engine)
        self.db = db

        # Get access token to perform request as a logged user
        settings = Settings()
        self.user_id, self.access_token = login_user(
            settings.keycloak_username_test,
            settings.keycloak_password_test,
            settings
        )


    def test_create_conversation(self):
        """
        Test user can create a conversation.
        :return:
        """
        id_conversation = str(uuid.uuid4())

        event = {
            "id": id_conversation,
            "name": "conversation test",
            "creator_id": self.user_id,
            "event": "userCreatedConversation",
            "created_at": "2023-08-28T07:23:31.353437Z"
        }

        asyncio.run(handle_event(event))

        # Verify conversation exists
        db_conversation = self.db.query(models.Conversation)\
            .filter(models.Conversation.id == id_conversation)\
            .first()

        assert db_conversation is not None


    def test_create_conversation_with_missing_fields(self):
        """
        Test user try to create a conversation. but fields are missing
        :return:
        """
        id_conversation = str(uuid.uuid4())

        event = {
            "id": id_conversation,
            "name": "conversation test",
            "event": "userCreatedConversation",
            "created_at": "2023-08-28T07:23:31.353437Z"
        }

        asyncio.run(handle_event(event))

        # Verify conversation exists
        db_conversation = self.db.query(models.Conversation)\
            .filter(models.Conversation.id == id_conversation)\
            .first()

        assert db_conversation is None


class TestRemoveConversation:
    def setup_method(self):
        """
        Setup database and create a conversation that is going to be used in next tests
        :return:
        """
        models.Base.metadata.create_all(bind=engine)
        self.db = db


        # Get access token to perform request as a logged user
        settings = Settings()
        self.user_id, self.access_token = login_user(
            settings.keycloak_username_test,
            settings.keycloak_password_test,
            settings
        )


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

    def test_user_delete_conversation(self):
        """
        Test a user can delete a conversation
        :return:
        """
        id_conversation = self.created_conversation['id']

        event = {
            "id": 1,
            "user_id": self.user_id,
            "conversation_id": id_conversation,
            "event": "userDeletedConversation",
            "created_at": "2023-08-30T12:13:56.008436Z"
        }
        asyncio.run(handle_event(event))

        # Verify conversation exists
        db_conversation = self.db.query(models.Conversation) \
            .filter(models.Conversation.id == id_conversation) \
            .first()

        assert db_conversation is None

    def test_user_delete_conversation_but_is_not_owner(self):
        """
        Test user try to delete a conversation but is not the owner
        :return:
        """
        self.setup_method()

        id_conversation = self.created_conversation['id']
        participant_id = "d8c2ec28-b43a-4259-99fa-924be1bf4ac0"

        event = {
            "id": 1,
            "user_id": participant_id,
            "conversation_id": id_conversation,
            "event": "userDeletedConversation",
            "created_at": "2023-08-30T12:13:56.008436Z"
        }
        asyncio.run(handle_event(event))

        # Verify conversation exists
        db_conversation = self.db.query(models.Conversation) \
            .filter(models.Conversation.id == id_conversation) \
            .first()

        assert db_conversation is not None

    def test_user_delete_conversation_with_missing_fields(self):
        """
        Test a user can delete a conversation but fields are missing in the event
        :return:
        """
        self.setup_method()
        id_conversation = self.created_conversation['id']

        event = {
            "id": 1,
            "user_id": self.user_id,
            "event": "userDeletedConversation",
            "created_at": "2023-08-30T12:13:56.008436Z"
        }
        asyncio.run(handle_event(event))

        # Verify conversation exists
        db_conversation = self.db.query(models.Conversation) \
            .filter(models.Conversation.id == id_conversation) \
            .first()

        assert db_conversation is not None







