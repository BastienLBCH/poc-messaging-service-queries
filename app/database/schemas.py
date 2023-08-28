from pydantic import BaseModel, ConfigDict
import datetime


class Conversation(BaseModel):
    model_config = ConfigDict(from_attributes = True)

    id: str
    name: str
    created_at: datetime.datetime


class Message(BaseModel):
    model_config = ConfigDict(from_attributes = True)

    id: str
    content: str
    user_id: str
    created_at: datetime.datetime
    conversation_id: str


class User(BaseModel):
    model_config = ConfigDict(from_attributes = True)

    id: str














