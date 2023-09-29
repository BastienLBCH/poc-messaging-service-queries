import json
import asyncio

from confluent_kafka import Consumer, OFFSET_BEGINNING

from app.settings import Settings
# from app.database import interface
from app.database.database import SessionLocal
# from app.websockets import ConnectionManager
# from app.main import connection_manager
# connection_manager = ConnectionManager()


db = SessionLocal()



def kafka_worker(handle_event, stop):
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

                print("Received event from topic {topic}: key = {key:12} value = {value:12}".format(
                    topic=msg.topic(), key=msg.key().decode('utf-8'), value=msg.value().decode('utf-8')))

                event = json.loads(msg.value().decode('utf-8'))
                asyncio.run(handle_event(event))

            if stop():
                break
        consumer.close()

    except Exception as e:
        print(e)






