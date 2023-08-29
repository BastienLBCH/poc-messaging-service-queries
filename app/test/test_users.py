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

class TestManipulatingUsers:
    def setup_method(self):
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

        user_in_conversation = False
        for user in db_conversation.users:
            if user.id == participant_id:
                user_in_conversation = True

        assert user_in_conversation is True


    def test_user_remove_participant_from_conversation(self):
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







