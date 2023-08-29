import json

from confluent_kafka import Consumer, OFFSET_BEGINNING

from app.settings import Settings
from app.database import interface
from app.database.database import SessionLocal

db = SessionLocal()


def handle_event(event):
    # print(event)
    if event['event'] == "userCreatedConversation":
        interface.create_conversation(event)
    elif event['event'] == "userAddedParticipantToConversation":
        interface.add_user_to_conversation(event)
    elif event['event'] == "userSentMessageToConversation":
        interface.add_message_to_conversation(event)
    elif event['event'] == "userRemovedParticipantToConversation":
        interface.remove_user_from_conversatin(event)


def kafka_worker():
    settings = Settings()

    conf = {
        'bootstrap.servers': settings.kafka_bootstrap_server,
        'group.id': settings.kafka_group_id,
        'auto.offset.reset': 'earliest'
    }
    topic = settings.kafka_topic

    consumer = Consumer(conf)

    consumer.subscribe([topic])

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                # print("Waiting...")
                pass
            elif msg.error():
                print(f"ERROR: {msg.error()}")
            else:
                # Extract the (optional) key and value, and print.

                print("Consumed event from topic {topic}: key = {key:12} value = {value:12}".format(
                    topic=msg.topic(), key=msg.key().decode('utf-8'), value=msg.value().decode('utf-8')))

                event = json.loads(msg.value().decode('utf-8'))
                handle_event(event)


    except Exception:
        pass






