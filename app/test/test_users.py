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

class TestAddUserToConversation:
    def setup_method(self):
        """
        Set up the database and conversation required for the following tests
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


    def test_add_user_to_conversation(self):
        """
        Test a user can add a participant to a conversation
        :return:
        """
        id_conversation = self.created_conversation['id']
        participant_id = "d8c2ec28-b43a-4259-99fa-924be1bf4ac0"
        event = {
            "id": 1,
            "user_id": "3866bd98-8dc2-4de6-aad0-8ef1a4e9a112",
            "participant_id": participant_id,
            "conversation_id": id_conversation,
            "event": "userAddedParticipantToConversation",
            "created_at": "2023-08-29T08:55:26.327046Z"
        }
        handle_event(event)

        db_conversation = self.db.query(models.Conversation) \
            .filter(models.Conversation.id == id_conversation) \
            .first()

        db_participant = self.db.query(models.User).filter(models.User.id==participant_id).first()

        assert db_participant in db_conversation.users


    def test_add_user_to_conversation_but_with_missing_fields(self):
        """
        Test a user can add a participant to a conversation but fields are missing
        :return:
        """
        self.setup_method()
        id_conversation = self.created_conversation['id']
        participant_id = "d8c2ec28-b43a-4259-99fa-924be1bf4ac0"
        event = {
            "id": 1,
            "participant_id": participant_id,
            "conversation_id": id_conversation,
            "event": "userAddedParticipantToConversation",
            "created_at": "2023-08-29T08:55:26.327046Z"
        }
        handle_event(event)

        db_conversation = self.db.query(models.Conversation) \
            .filter(models.Conversation.id == id_conversation) \
            .first()

        db_participant = self.db.query(models.User).filter(models.User.id==participant_id).first()

        assert db_participant not in db_conversation.users


    def test_user_add_himself_to_conversation(self):
        """
        Test that a user can't add himself to a conversation
        :return:
        """
        id_conversation = self.created_conversation['id']
        participant_id = "d8c2ec28-b43a-4259-99fa-924be1bf4ac0"
        user_id = "3866bd98-8dc2-4de6-aad0-8ef1a4e9a112"
        event = {
            "id": 1,
            "user_id": user_id,
            "participant_id": user_id,
            "conversation_id": id_conversation,
            "event": "userAddedParticipantToConversation",
            "created_at": "2023-08-29T08:55:26.327046Z"
        }
        handle_event(event)

        db_conversation = self.db.query(models.Conversation) \
            .filter(models.Conversation.id == id_conversation) \
            .first()

        db_user = self.db.query(models.User).filter(models.User.id==user_id).first()
        user_in_conversation_counter = db_conversation.users.count(db_user)

        assert user_in_conversation_counter == 1


    def test_user_add_participant_already_member_to_conversation(self):
        """
        Test a user can't add a participant twice
        :return:
        """
        id_conversation = self.created_conversation['id']
        participant_id = "d8c2ec28-b43a-4259-99fa-924be1bf4ac0"
        event = {
            "id": 1,
            "user_id": "3866bd98-8dc2-4de6-aad0-8ef1a4e9a112",
            "participant_id": participant_id,
            "conversation_id": id_conversation,
            "event": "userAddedParticipantToConversation",
            "created_at": "2023-08-29T08:55:26.327046Z"
        }
        handle_event(event)

        id_conversation = self.created_conversation['id']
        participant_id = "d8c2ec28-b43a-4259-99fa-924be1bf4ac0"
        event = {
            "id": 1,
            "user_id": "3866bd98-8dc2-4de6-aad0-8ef1a4e9a112",
            "participant_id": participant_id,
            "conversation_id": id_conversation,
            "event": "userAddedParticipantToConversation",
            "created_at": "2023-08-29T08:55:26.327046Z"
        }
        handle_event(event)

        db_conversation = self.db.query(models.Conversation) \
            .filter(models.Conversation.id == id_conversation) \
            .first()

        db_participant = self.db.query(models.User).filter(models.User.id == participant_id).first()
        user_in_conversation_counter = db_conversation.users.count(db_participant)

        assert user_in_conversation_counter == 1


class TestRemoveUserFromConversation:
    def setup_method(self):
        """
        Setup a conversation then add a user to it for next tests
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

        # Add the user to the conversation
        id_conversation = self.created_conversation['id']
        self.participant_id = "d8c2ec28-b43a-4259-99fa-924be1bf4ac0"
        event = {
            "id": 1,
            "user_id": "3866bd98-8dc2-4de6-aad0-8ef1a4e9a112",
            "participant_id": self.participant_id,
            "conversation_id": id_conversation,
            "event": "userAddedParticipantToConversation",
            "created_at": "2023-08-29T08:55:26.327046Z"
        }
        handle_event(event)


    def test_user_remove_participant_from_conversation(self):
        """
        Test that a user can remove another from a conversation
        :return:
        """
        id_conversation = self.created_conversation['id']
        participant_id = "d8c2ec28-b43a-4259-99fa-924be1bf4ac0"
        event = {
            "id": 1,
            "user_id": "3866bd98-8dc2-4de6-aad0-8ef1a4e9a112",
            "participant_id": participant_id,
            "conversation_id": id_conversation,
            "event": "userRemovedParticipantToConversation",
            "created_at": "2023-08-29T08:55:26.599274Z"
        }

        db_conversation = db.query(models.Conversation) \
            .filter(models.Conversation.id == id_conversation) \
            .first()

        db_participant = db.query(models.User)\
            .filter(models.User.id==participant_id)\
            .first()

        if not db_participant in db_conversation.users:
            db_conversation.users.append(db_participant)
            db.commit()

        handle_event(event)

        db.refresh(db_conversation)
        participant_still_in_conversation = db_participant in db_conversation.users
        assert participant_still_in_conversation is False


    def test_participant_cant_remove_owner_from_conversation(self):
        """
        Test that a user can remove another from a conversation
        :return:
        """
        id_conversation = self.created_conversation['id']
        participant_id = "d8c2ec28-b43a-4259-99fa-924be1bf4ac0"
        owner_id = self.created_conversation['creator_id']

        event = {
            "id": 1,
            "user_id": participant_id,
            "participant_id": owner_id,
            "conversation_id": id_conversation,
            "event": "userRemovedParticipantToConversation",
            "created_at": "2023-08-29T08:55:26.599274Z"
        }

        db_conversation = db.query(models.Conversation) \
            .filter(models.Conversation.id == id_conversation) \
            .first()

        db_user = db.query(models.User)\
            .filter(models.User.id==owner_id)\
            .first()

        if not db_user in db_conversation.users:
            db_conversation.users.append(db_user)
            db.commit()

        handle_event(event)

        db.refresh(db_conversation)
        participant_still_in_conversation = db_user in db_conversation.users
        assert participant_still_in_conversation is True







