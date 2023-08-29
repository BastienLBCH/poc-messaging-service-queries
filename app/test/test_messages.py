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

class TestMessages:
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

    def test_user_sent_message(self):
        id_conversation = self.created_conversation['id']
        message_content = ''.join(random.choice(string.ascii_letters) for i in range(25))
        event = {
            "id": 1,
            "user_id": "3866bd98-8dc2-4de6-aad0-8ef1a4e9a112",
            "conversation_id": id_conversation,
            "message_content": message_content,
            "event": "userSentMessageToConversation",
            "created_at": "2023-08-29T08:55:26.694214Z"
        }
        handle_event(event)

        db_conversation = db.query(models.Conversation) \
            .filter(models.Conversation.id == id_conversation) \
            .first()

        message_is_in_conversation = False
        for message in db_conversation.messages:
            if message.content == message_content:
                message_is_in_conversation = True

        assert message_is_in_conversation is True