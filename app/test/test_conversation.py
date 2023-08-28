import json
import uuid
import datetime
from multiprocessing import Process

import pytest
from fastapi.testclient import TestClient
from confluent_kafka import Producer

from app.main import app
from app.settings import Settings
from app.database import schemas, models
from app.database.database import SessionLocal
from app import kafka_client


settings = Settings()

conf = {
    'bootstrap.servers': settings.kafka_bootstrap_server
}
topic = settings.kafka_topic

producer = Producer(conf)

process = Process(target=kafka_client.kafka_worker, args=())
db = SessionLocal()


class TestConversation:
    def setup_method(self):
        self.process = Process(target=kafka_client.kafka_worker, args=())
        self.process.start()

    def test_create_conversation(self):
        id_conversation = str(uuid.uuid4())
        conversation = schemas.Conversation(
            id=id_conversation,
            name="conversation test",
            created_at=datetime.datetime.now()
        )
        key = "event"

        # print(str(conversation))
        # print(f"\n###\n{json.loads(conversation.model_dump_json())['id']}\n###\n")
        producer.produce(topic, str(conversation.model_dump_json()), key)

        # Block until the messages are sent.
        producer.poll(10000)
        producer.flush()

        # Verify conversation exists
        db_conversation = db.query(models.Conversation)\
            .filter(models.Conversation.id == id_conversation)\
            .first()

        assert db_conversation is not None

    def teardown_method(self):
        self.process.terminate()














# value = {"id": "5423437d-6cc3-424f-994d-97a7d4fad611", "name": "conversation_test", "creator_id": "3866bd98-8dc2-4de6-aad0-8ef1a4e9a112", "event": "userCreatedConversation", "created_at": "2023-08-28T07:23:31.353437Z"}