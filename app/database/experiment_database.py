# from database import SessionLocal, engine
# from models import Users, Conversations
import datetime


from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


mtmUserConversations = Table(
    "mtmUserConversations",
    Base.metadata,
    Column("user_id", ForeignKey("User.id"), primary_key=True),
    Column("conversation_id", ForeignKey("Conversation.id"), primary_key=True)
)


class User(Base):
    __tablename__ = 'User'

    id = Column(String, primary_key=True)

    conversations = relationship('Conversation', secondary='mtmUserConversations', back_populates='users')
    messages = relationship('Message', back_populates='user', cascade='all, delete-orphan')


class Conversation(Base):
    __tablename__ = 'Conversation'

    id = Column(String, primary_key=True)
    name = Column(String)
    created_at = Column(DateTime, default=func.now())

    users = relationship('User', secondary='mtmUserConversations', back_populates='conversations')
    messages = relationship('Message', back_populates='conversation', cascade='all, delete-orphan')


class Message(Base):
    __tablename__ = 'Message'

    id = Column(String, primary_key=True)
    content = Column(String)
    created_at = Column(DateTime, default=func.now())

    user_id = Column(String, ForeignKey("User.id"))
    conversation_id = Column(String, ForeignKey("Conversation.id"))

    user = relationship('User', back_populates='messages')
    conversation = relationship('Conversation', back_populates='messages')


Base.metadata.create_all(bind=engine)
db = SessionLocal()

db_user_1 = User(id="azer")
db.add(db_user_1)

db_user_2 = User(id="zert")
db.add(db_user_2)

db_user_3 = User(id="erty")
db.add(db_user_3)


db_conversation_1 = Conversation(id='qsdf', name='conv 1')
db.add(db_conversation_1)

db_conversation_2 = Conversation(id='dsfg', name='conv 2')
db.add(db_conversation_2)

db_conversation_3 = Conversation(id='dfgh', name='conv 3')
db.add(db_conversation_3)

db_conversation_1.users = [db_user_1, db_user_2, db_user_3]
db_conversation_2.users = [db_user_1, db_user_2, db_user_3]
db_conversation_3.users = [db_user_1, db_user_2, db_user_3]

db_message_1 = Message(
    id='jklm',
    content="Salut les amis ! Ça va ?",
    user = db_user_1,
    conversation = db_conversation_1
)

db_message_2 = Message(
    id='hjkl',
    content="Moi j'ai trop la forme !",
    user = db_user_1,
    conversation = db_conversation_1
)
db.add(db_message_1)
db.add(db_message_2)

db.commit()

db_users = db.query(User).offset(0).limit(10).all()
for user in db_users:
    print(f"User {user.id} in conversations : ")
    for conversation in user.conversations:
        print(conversation.name)
    print("\n")


db_conversations = db.query(Conversation).offset(0).limit(10).all()
for conversation in db_conversations:
    print(f"In conversation {conversation.name} users :")
    for user in conversation.users:
        print(user.id)
        for message in user.messages:
            if message.conversation == conversation:
                print(f'> {message.content}')
        print("\n")
    print("\n")

# db.delete(db_user_1)
# db.delete(db_message_1)
# db.delete(db_conversation_1)

event = {
    "id": "746048a5-296f-4365-a39a-57d37136ccda",
    "name": "test",
    "creator_id": "3866bd98-8dc2-4de6-aad0-8ef1a4e9a112",
    "event": "userCreatedConversation",
    "created_at": "2023-08-28T11:26:21.967820Z"
}

db_user = db.query(User).filter(User.id==event['creator_id']).first()
if db_user is None:
    db_user = User(id=event['creator_id'])
    db.add(db_user)

db_conversation = db.query(Conversation).filter(Conversation.id == event['id']).first()
if db_conversation is None:
    db_conversation = Conversation(id=event['id'], name=event['name'], created_at=datetime.datetime.fromisoformat(event['created_at']))
    db_conversation.users.append(db_user)
    db.add(db_conversation)
db.commit()

db_conversation_1.users.remove(db_user_1)

print(db.query(Conversation).filter(Conversation.id=="mabite").first())

db.commit()






