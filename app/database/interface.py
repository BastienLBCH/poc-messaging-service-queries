import datetime

from sqlalchemy.orm import Session
from app.database import models, schemas
from app.database.database import SessionLocal

db = SessionLocal()


def create_conversation(event: dict):
    db_user = db.query(models.User).filter(models.User.id==event['creator_id']).first()
    if db_user is None:
        db_user = models.User(id=event['creator_id'])
        db.add(db_user)

    db_conversation = db.query(models.Conversation).filter(models.Conversation.id == event['id']).first()
    if db_conversation is None:
        db_conversation = models.Conversation(id=event['id'], name=event['name'], created_at=datetime.datetime.fromisoformat(event['created_at']))
        db_conversation.users.append(db_user)
        db.add(db_conversation)
    db.commit()

    return True


def add_user_to_conversation(event: dict):
    db_user = db.query(models.User).filter(models.User.id == event['participant_id']).first()
    if db_user is None:
        db_user = models.User(id=event['participant_id'])
        db.add(db_user)

    db_conversation = db.query(models.Conversation).filter(models.Conversation.id == event['conversation_id']).first()
    if db_conversation is not None:
        db_conversation.users.append(db_user)
        db.commit()


def add_message_to_conversation(event: dict):
    db_user = db.query(models.User)\
        .filter(models.User.id == event["user_id"])\
        .first()

    if db_user is None:
        db_user = models.User(id=event['user_id'])
        db.add(db_user)

    db_conversation = db.query(models.Conversation)\
        .filter(models.Conversation.id == event['conversation_id'])\
        .first()
    if db_conversation is not None:
        db_message = models.Message(
            content=event["message_content"],
            created_at=datetime.datetime.fromisoformat(event["created_at"]),
            user=db_user,
            conversation=db_conversation
        )
        db.add(db_message)
        db.commit()




