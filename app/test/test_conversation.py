import random
import string
import uuid
import datetime
import json

from app.database import schemas, models
from app.database.database import SessionLocal, engine
from app.kafka_client import handle_event

from app.main import app

db = SessionLocal()


class TestCreateConversation:
    def setup_method(self):
        """
        Initiate database for creating conversation test
        :return:
        """
        models.Base.metadata.create_all(bind=engine)
        self.db = db


    def test_create_conversation(self):
        """
        Test user can create a conversation.
        :return:
        """
        id_conversation = str(uuid.uuid4())

        event = {
            "id": id_conversation,
            "name": "conversation test",
            "creator_id": "3866bd98-8dc2-4de6-aad0-8ef1a4e9a112",
            "event": "userCreatedConversation",
            "created_at": "2023-08-28T07:23:31.353437Z"
        }

        handle_event(event)

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

        handle_event(event)

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

        # Prepare conversation for further tests
        id_conversation = str(uuid.uuid4())
        self.created_conversation = {
            "id": id_conversation,
            "name": "conversation test",
            "creator_id": "3866bd98-8dc2-4de6-aad0-8ef1a4e9a112",
            "event": "userCreatedConversation",
            "created_at": "2023-08-28T07:23:31.353437Z"
        }
        handle_event(self.created_conversation)

    def test_user_delete_conversation(self):
        """
        Test a user can delete a conversation
        :return:
        """
        id_conversation = self.created_conversation['id']
        user_id = self.created_conversation['creator_id']

        event = {
            "id": 1,
            "user_id": user_id,
            "conversation_id": id_conversation,
            "event": "userDeletedConversation",
            "created_at": "2023-08-30T12:13:56.008436Z"
        }
        handle_event(event)

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
        user_id = self.created_conversation['creator_id']
        participant_id = "d8c2ec28-b43a-4259-99fa-924be1bf4ac0"

        event = {
            "id": 1,
            "user_id": participant_id,
            "conversation_id": id_conversation,
            "event": "userDeletedConversation",
            "created_at": "2023-08-30T12:13:56.008436Z"
        }
        handle_event(event)

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
        user_id = self.created_conversation['creator_id']

        event = {
            "id": 1,
            "user_id": user_id,
            "event": "userDeletedConversation",
            "created_at": "2023-08-30T12:13:56.008436Z"
        }
        handle_event(event)

        # Verify conversation exists
        db_conversation = self.db.query(models.Conversation) \
            .filter(models.Conversation.id == id_conversation) \
            .first()

        assert db_conversation is not None







