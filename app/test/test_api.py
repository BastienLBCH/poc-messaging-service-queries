import requests
import uuid
import asyncio

from fastapi.testclient import TestClient

from app.settings import Settings
from app.main import handle_event
from app.main import app
from app import utils


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


class TestAPIGetMessages:
    def setup_method(self):
        """
        Set up the test case to get messages from a conversation
        :return:
        """
        # Get access token to perform request as a logged user
        settings = Settings()
        self.user_id_1, self.access_token = login_user(
            settings.keycloak_username_test,
            settings.keycloak_password_test,
            settings
        )

        self.user_id_2, self.access_token_user_2 = login_user(
            settings.keycloak_username_test_2,
            settings.keycloak_password_test,
            settings
        )


        # Set up a conversation
        conversation_id = str(uuid.uuid4())
        self.created_conversation = {
            "id": conversation_id,
            "name": "conversation test api",
            "creator_id": self.user_id_1,
            "event": "userCreatedConversation",
            "created_at": "2023-08-28T07:23:31.353437Z"
        }

        asyncio.run(handle_event(self.created_conversation))

        # Add messages to it
        self.sent_message = {
            "user_id": self.user_id_1,
            "conversation_id": conversation_id,
            "message_content": "Test Message",
            "event": "userSentMessageToConversation",
            "created_at": "2023-08-29T08:55:26.694214Z"
        }
        asyncio.run(handle_event(self.sent_message))

        # create client
        self.client = TestClient(app)

    def test_get_messages(self):
        """
        Test that a user can get its messages back from conversations
        :return:
        """
        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }
        response = self.client.get(f'/conversations/{self.created_conversation["id"]}', headers=headers)

        keys = ['id', 'content', 'user_id', 'created_at', 'conversation_id']
        response_is_complete = True
        for key in keys:
            if not key in response.json()[0]:
                response_is_complete = False

        assert response.status_code == 200
        assert response_is_complete

    def test_user_not_in_conversation_cant_get_messages(self):
        """
        Test that a user not in a conversation can't get messages from it
        :return:
        """
        headers = {
            'Authorization': f'Bearer {self.access_token_user_2}'
        }
        response = self.client.get(f'/conversations/{self.created_conversation["id"]}', headers=headers)

        assert response.status_code == 400



class TestAPIGetConversations:
    def setup_method(self):
        """
        Set up the test case to get all conversations from a user
        :return:
        """
        # Get access token to perform request as a logged user
        settings = Settings()


        settings = Settings()
        self.user_id_1, self.access_token = login_user(
            settings.keycloak_username_test,
            settings.keycloak_password_test,
            settings
        )

        self.user_id_2, self.access_token_user_2 = login_user(
            settings.keycloak_username_test_2,
            settings.keycloak_password_test,
            settings
        )

        # Set up a conversation
        conversation_id = str(uuid.uuid4())
        self.created_conversation = {
            "id": conversation_id,
            "name": "conversation test api",
            "creator_id": self.user_id_1,
            "event": "userCreatedConversation",
            "created_at": "2023-08-28T07:23:31.353437Z"
        }

        conversation_id = str(uuid.uuid4())
        self.created_conversation_2 = {
            "id": conversation_id,
            "name": "conversation test api",
            "creator_id": self.user_id_2,
            "event": "userCreatedConversation",
            "created_at": "2023-08-28T07:23:31.353437Z"
        }
        asyncio.run(handle_event(self.created_conversation))
        asyncio.run(handle_event(self.created_conversation_2))

        self.client = TestClient(app)


    def test_user_can_get_conversation(self):
        """
        Test that the endpoint returns conversations associated to a specific user
        :return:
        """
        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }
        response = self.client.get(f'/conversations', headers=headers)
        assert response.status_code == 200

        conversation_created_in_response = False
        for conversation in response.json():
            if conversation['id'] == self.created_conversation['id']:
                conversation_created_in_response = True

        assert conversation_created_in_response is True


    def test_user_doesnt_get_conversations_his_not_inside(self):
        """
        Test that the endpoint doesn't return conversations a user is not into
        :return:
        """
        headers = {
            'Authorization': f'Bearer {self.access_token_user_2}'
        }
        response = self.client.get(f'/conversations', headers=headers)
        assert response.status_code == 200

        conversation_created_in_response = False
        for conversation in response.json():
            if conversation['id'] == self.created_conversation['id']:
                conversation_created_in_response = True

        assert conversation_created_in_response is False



class TestAPIGetConversationMembers:
    def setup_method(self):
        """
        Set up the test case to get all conversations from a user
        :return:
        """
        # Get access token to perform request as a logged user
        settings = Settings()


        settings = Settings()
        self.user_id_1, self.access_token = login_user(
            settings.keycloak_username_test,
            settings.keycloak_password_test,
            settings
        )

        self.user_id_2, self.access_token_user_2 = login_user(
            settings.keycloak_username_test_2,
            settings.keycloak_password_test,
            settings
        )

        # Set up a conversation
        conversation_id = str(uuid.uuid4())
        self.created_conversation = {
            "id": conversation_id,
            "name": "conversation test api",
            "creator_id": self.user_id_1,
            "event": "userCreatedConversation",
            "created_at": "2023-08-28T07:23:31.353437Z"
        }
        asyncio.run(handle_event(self.created_conversation))

        # Set up a second conversation
        conversation_id = str(uuid.uuid4())
        self.created_conversation_2 = {
            "id": conversation_id,
            "name": "conversation test api",
            "creator_id": self.user_id_2,
            "event": "userCreatedConversation",
            "created_at": "2023-08-28T07:23:31.353437Z"
        }
        asyncio.run(handle_event(self.created_conversation))

        self.client = TestClient(app)

    def test_user_can_get_participants(self):
        """
        Test that authentified user can get the participants
        :return:
        """
        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }
        conversation_id = self.created_conversation['id']
        response = self.client.get(f'/conversations/{conversation_id}/members', headers=headers)

        assert response.status_code == 200
        assert response.json()[0]['id'] == self.created_conversation['creator_id']


    def test_user_cant_get_participant_if_not_in_conversation(self):
        """
        test that a user can't get the participants from a conversation he's not inside
        :return:
        """
        headers = {
            'Authorization': f'Bearer {self.access_token_user_2}'
        }
        conversation_id = self.created_conversation['id']
        response = self.client.get(f'/conversations/{conversation_id}/members', headers=headers)

        assert response.status_code == 400

