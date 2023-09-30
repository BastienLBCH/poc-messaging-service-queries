import uuid
import requests
import asyncio

from app.database import schemas, models
from app.database.database import SessionLocal, engine
from app.main import handle_event
from app.settings import Settings
from app import utils


db = SessionLocal()


def login_user(username: str, password: str, settings: Settings):
    """
    Return access token and user_id for specific user
    :param username:
    :param password:
    :return:
    """
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = f"client_id={settings.keycloak_client_id}&username={username}&password={password}&grant_type=password"
    r = requests.post(headers=headers, data=data, url=settings.keycloak_token_url)
    access_token = r.json()["access_token"]
    user_id = utils.get_userid_from_token(access_token)
    return user_id, access_token


class TestAddUserToConversation:
    def setup_method(self):
        """
        Set up the database and conversation required for the following tests
        :return:
        """
        models.Base.metadata.create_all(bind=engine)
        self.db = db

        settings = Settings()
        self.user_id, self.access_token = login_user(settings.keycloak_username_test, settings.keycloak_password_test, settings)

        # Prepare conversation for further tests
        id_conversation = str(uuid.uuid4())
        self.created_conversation = {
            "id": id_conversation,
            "name": "conversation test",
            "creator_id": self.user_id,
            "event": "userCreatedConversation",
            "created_at": "2023-08-28T07:23:31.353437Z"
        }
        asyncio.run(handle_event(self.created_conversation))


    def test_add_user_to_conversation(self):
        """
        Test a user can add a participant to a conversation
        :return:
        """
        id_conversation = self.created_conversation['id']
        participant_id = "d8c2ec28-b43a-4259-99fa-924be1bf4ac0"
        event = {
            "id": 1,
            "user_id": self.user_id,
            "participant_id": participant_id,
            "conversation_id": id_conversation,
            "event": "userAddedParticipantToConversation",
            "created_at": "2023-08-29T08:55:26.327046Z"
        }
        asyncio.run(handle_event(event))

        db_conversation = self.db.query(models.Conversation) \
            .filter(models.Conversation.id == id_conversation) \
            .first()

        db_participant = self.db.query(models.User).filter(models.User.id==participant_id).first()

        assert db_participant in db_conversation.users


    def test_add_user_to_conversation_but_with_missing_fields(self):
        """
        Test a user can add a participant to a conversation but fields are missing
        :return:
        """
        self.setup_method()
        id_conversation = self.created_conversation['id']
        participant_id = "d8c2ec28-b43a-4259-99fa-924be1bf4ac0"
        event = {
            "id": 1,
            "participant_id": participant_id,
            "conversation_id": id_conversation,
            "event": "userAddedParticipantToConversation",
            "created_at": "2023-08-29T08:55:26.327046Z"
        }
        asyncio.run(handle_event(event))

        db_conversation = self.db.query(models.Conversation) \
            .filter(models.Conversation.id == id_conversation) \
            .first()

        db_participant = self.db.query(models.User).filter(models.User.id==participant_id).first()

        assert db_participant not in db_conversation.users


    def test_user_add_himself_to_conversation(self):
        """
        Test that a user can't add himself to a conversation
        :return:
        """
        id_conversation = self.created_conversation['id']
        event = {
            "id": 1,
            "user_id": self.user_id,
            "participant_id": self.user_id,
            "conversation_id": id_conversation,
            "event": "userAddedParticipantToConversation",
            "created_at": "2023-08-29T08:55:26.327046Z"
        }
        asyncio.run(handle_event(event))

        db_conversation = self.db.query(models.Conversation) \
            .filter(models.Conversation.id == id_conversation) \
            .first()

        db_user = self.db.query(models.User).filter(models.User.id==self.user_id).first()
        user_in_conversation_counter = db_conversation.users.count(db_user)

        assert user_in_conversation_counter == 1


    def test_user_add_participant_already_member_to_conversation(self):
        """
        Test a user can't add a participant twice
        :return:
        """
        id_conversation = self.created_conversation['id']
        participant_id = "d8c2ec28-b43a-4259-99fa-924be1bf4ac0"
        event = {
            "id": 1,
            "user_id": self.user_id,
            "participant_id": participant_id,
            "conversation_id": id_conversation,
            "event": "userAddedParticipantToConversation",
            "created_at": "2023-08-29T08:55:26.327046Z"
        }
        asyncio.run(handle_event(event))

        id_conversation = self.created_conversation['id']
        participant_id = "d8c2ec28-b43a-4259-99fa-924be1bf4ac0"
        event = {
            "id": 1,
            "user_id": self.user_id,
            "participant_id": participant_id,
            "conversation_id": id_conversation,
            "event": "userAddedParticipantToConversation",
            "created_at": "2023-08-29T08:55:26.327046Z"
        }
        asyncio.run(handle_event(event))

        db_conversation = self.db.query(models.Conversation) \
            .filter(models.Conversation.id == id_conversation) \
            .first()

        db_participant = self.db.query(models.User).filter(models.User.id == participant_id).first()
        user_in_conversation_counter = db_conversation.users.count(db_participant)

        assert user_in_conversation_counter == 1


class TestRemoveUserFromConversation:
    def setup_method(self):
        """
        Setup a conversation then add a user to it for next tests
        :return:
        """
        models.Base.metadata.create_all(bind=engine)
        self.db = db

        settings = Settings()
        self.user_id, self.access_token = login_user(
            settings.keycloak_username_test,
            settings.keycloak_password_test,
            settings
        )

        self.participant_id, self.participant_token = login_user(
            settings.keycloak_username_test_2,
            settings.keycloak_password_test,
            settings
        )

        # Prepare conversation for further tests
        id_conversation = str(uuid.uuid4())
        self.created_conversation = {
            "id": id_conversation,
            "name": "conversation test",
            "creator_id": self.user_id,
            "event": "userCreatedConversation",
            "created_at": "2023-08-28T07:23:31.353437Z"
        }
        asyncio.run(handle_event(self.created_conversation))

        # Add the user to the conversation
        id_conversation = self.created_conversation['id']
        event = {
            "id": 1,
            "user_id": self.user_id,
            "participant_id": self.participant_id,
            "conversation_id": id_conversation,
            "event": "userAddedParticipantToConversation",
            "created_at": "2023-08-29T08:55:26.327046Z"
        }
        asyncio.run(handle_event(event))


    def test_user_remove_participant_from_conversation(self):
        """
        Test that a user can remove another from a conversation
        :return:
        """
        id_conversation = self.created_conversation['id']
        event = {
            "id": 1,
            "user_id": self.user_id,
            "participant_id": self.participant_id,
            "conversation_id": id_conversation,
            "event": "userRemovedParticipantToConversation",
            "created_at": "2023-08-29T08:55:26.599274Z"
        }

        db_conversation = db.query(models.Conversation) \
            .filter(models.Conversation.id == id_conversation) \
            .first()

        db_participant = db.query(models.User)\
            .filter(models.User.id==self.participant_id)\
            .first()

        if not db_participant in db_conversation.users:
            db_conversation.users.append(db_participant)
            db.commit()

        asyncio.run(handle_event(event))

        db.refresh(db_conversation)
        participant_still_in_conversation = db_participant in db_conversation.users
        assert participant_still_in_conversation is False


    def test_participant_cant_remove_owner_from_conversation(self):
        """
        Test that a user can remove another from a conversation
        :return:
        """
        id_conversation = self.created_conversation['id']

        event = {
            "id": 1,
            "user_id": self.participant_id,
            "participant_id": self.user_id,
            "conversation_id": id_conversation,
            "event": "userRemovedParticipantToConversation",
            "created_at": "2023-08-29T08:55:26.599274Z"
        }

        db_conversation = db.query(models.Conversation) \
            .filter(models.Conversation.id == id_conversation) \
            .first()

        db_user = db.query(models.User)\
            .filter(models.User.id==self.user_id)\
            .first()

        if not db_user in db_conversation.users:
            db_conversation.users.append(db_user)
            db.commit()

        asyncio.run(handle_event(event))

        db.refresh(db_conversation)
        participant_still_in_conversation = db_user in db_conversation.users
        assert participant_still_in_conversation is True







