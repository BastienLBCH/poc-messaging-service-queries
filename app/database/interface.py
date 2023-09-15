import datetime

from sqlalchemy.orm import Session
from app.database import models, schemas
from app.database.database import SessionLocal

db = SessionLocal()


def event_contains_all_required_fields(event: dict, required_keys: list):
    """
    Verify that the event is complete
    :param event:
    :param required_keys:
    :return:
    """
    for key in required_keys:
        if key not in event:
            return False
    return True


def create_conversation(event: dict):
    """
    Create a new conversation object from the event
    :param event:
    :return:
    """
    required_keys = ['id', 'name', 'creator_id', 'created_at']
    if event_contains_all_required_fields(event, required_keys):
        db_user = db.query(models.User).filter(models.User.id==event['creator_id']).first()
        if db_user is None:
            db_user = models.User(id=event['creator_id'])
            db.add(db_user)

        db_conversation = db.query(models.Conversation).filter(models.Conversation.id == event['id']).first()
        if db_conversation is None:
            db_conversation = models.Conversation(
                id=event['id'],
                name=event['name'],
                created_at=datetime.datetime.fromisoformat(event['created_at'])
            )
            db_conversation.users.append(db_user)
            db_conversation.owner = db_user
            db.add(db_conversation)
        db.commit()

        return True
    return False


def add_user_to_conversation(event: dict):
    required_keys = ['user_id', 'participant_id', 'conversation_id']
    if event_contains_all_required_fields(event, required_keys):
        db_user = db.query(models.User).filter(models.User.id==event['user_id']).first()
        db_participant = db.query(models.User).filter(models.User.id == event['participant_id']).first()
        if db_participant is None:
            db_participant = models.User(id=event['participant_id'])
            db.add(db_participant)

        db_conversation = db.query(models.Conversation).filter(models.Conversation.id == event['conversation_id']).first()
        if db_conversation is not None and db_conversation.owner == db_user and db_participant not in db_conversation.users:
            db_conversation.users.append(db_participant)
            db.commit()
            return True
    return False


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


def remove_user_from_conversation(event: dict):
    """
    Remove a user from a conversation
    :param event:
    :return:
    """
    db_user = db.query(models.User).filter(models.User.id==event['user_id']).first()
    db_conversation = db.query(models.Conversation).filter(models.Conversation.id==event['conversation_id']).first()

    if db_conversation.owner == db_user:
        db_participant = db.query(models.User).filter(models.User.id==event['participant_id']).first()
        if db_participant in db_conversation.users:
            db_conversation.users.remove(db_participant)
            db.commit()


def delete_conversation(event: dict):
    """
    Delete a specific conversation
    :param event:
    :return:
    """
    required_keys = ['user_id', 'conversation_id']
    if event_contains_all_required_fields(event, required_keys):
        db_user = db.query(models.User).filter(models.User.id==event['user_id']).first()
        db_conversation = db.query(models.Conversation).filter(models.Conversation.id==event['conversation_id']).first()

        if db_conversation.owner == db_user:
            db.delete(db_conversation)
            db.commit()
            return True
    return False


def get_all_conversations_from_user(user_id: str):
    """
    Get all conversations from a specific user
    :param user_id:
    :return:
    """
    db_user = db.query(models.User).filter(models.User.id==user_id).first()
    return db_user.conversations


def get_all_messages_from_conversation(user_id: str, conversation_id: str):
    """
    Get all messages from a conversation
    :param user_id:
    :param conversation_id:
    :return:
    """
    db_user = db.query(models.User).filter(models.User.id==user_id).first()
    db_conversation = db.query(models.Conversation).filter(models.Conversation.id==conversation_id).first()

    if db_user in db_conversation.users:
        db_messages = db.query(models.Message).filter(models.Message.conversation_id==conversation_id).order_by(models.Message.created_at).all()
        return db_messages
    return None


def get_all_users_ids_from_conversation(conversation_id: str):
    """
    Return all users ids from a specific conversation
    :param conversation_id: str conversation id
    :return:
    """
    users_id_list: list = []

    db_conversation = db.query(models.Conversation).filter(models.Conversation.id==conversation_id).first()
    for user in db_conversation.users:
        users_id_list.append(user.id)

    return users_id_list





