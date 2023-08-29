from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


from app.database.database import Base


mtmUserConversations = Table(
    "mtmUserConversations",
    Base.metadata,
    Column("user_id", ForeignKey("User.id"), primary_key=True),
    Column("conversation_id", ForeignKey("Conversation.id"), primary_key=True)
)


class User(Base):
    __tablename__ = 'User'

    id = Column(String, primary_key=True)

    owned_conversations = relationship('Conversation', back_populates='owner')
    conversations = relationship('Conversation', secondary='mtmUserConversations', back_populates='users')
    messages = relationship('Message', back_populates='user', cascade='all, delete-orphan')


class Conversation(Base):
    __tablename__ = 'Conversation'

    id = Column(String, primary_key=True)
    name = Column(String)
    created_at = Column(DateTime, default=func.now())
    owner_id = Column(String, ForeignKey("User.id"))

    owner = relationship('User', back_populates='owned_conversations')
    users = relationship('User', secondary='mtmUserConversations', back_populates='conversations')
    messages = relationship('Message', back_populates='conversation', cascade='all, delete-orphan')


class Message(Base):
    __tablename__ = 'Message'

    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(String)
    created_at = Column(DateTime, default=func.now())

    user_id = Column(String, ForeignKey("User.id"))
    conversation_id = Column(String, ForeignKey("Conversation.id"))

    user = relationship('User', back_populates='messages')
    conversation = relationship('Conversation', back_populates='messages')


