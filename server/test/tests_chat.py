import pytest
import json
from http import HTTPStatus
from your_flask_app import app  # replace 'your_flask_app' with the actual name of your Flask app module
from your_flask_app.models.models import Mentors, Mentees, Community, ChatConnection, CommunityMember, Message
from flask_jwt_extended import create_access_token

DUMMY_USERNAME = "dummy_user"
DUMMY_EMAIL = "dummy@example.com"
DUMMY_PASSWORD = "password"
DUMMY_MENTOR_ID = 1
DUMMY_MENTEE_ID = 2
DUMMY_COMMUNITY_ID = 1

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def create_jwt_token(user_id, user_type):
    identity = {'id': user_id, 'type': user_type}
    token = create_access_token(identity=identity)
    return token

def test_connect_mentee_mentor(client):
    mentor_jwt = create_jwt_token(DUMMY_MENTOR_ID, 'mentor')
    mentee_jwt = create_jwt_token(DUMMY_MENTEE_ID, 'mentee')

    response = client.post(
        "/chats/connect",
        data=json.dumps({"mentor_id": DUMMY_MENTOR_ID}),
        content_type="application/json",
        headers={"Authorization": f"Bearer {mentee_jwt}"}
    )

    data = json.loads(response.data.decode())
    assert response.status_code == HTTPStatus.CREATED
    assert data["success"] is True

def test_mentor_join_community(client):
    mentor_jwt = create_jwt_token(DUMMY_MENTOR_ID, 'mentor')

    response = client.post(
        "/chats/mentor/join",
        data=json.dumps({"community_id": DUMMY_COMMUNITY_ID}),
        content_type="application/json",
        headers={"Authorization": f"Bearer {mentor_jwt}"}
    )

    data = json.loads(response.data.decode())
    assert response.status_code == HTTPStatus.OK
    assert data["success"] is True

def test_mentee_join_community(client):
    mentee_jwt = create_jwt_token(DUMMY_MENTEE_ID, 'mentee')

    response = client.post(
        "/chats/mentee/join",
        data=json.dumps({"community_id": DUMMY_COMMUNITY_ID}),
        content_type="application/json",
        headers={"Authorization": f"Bearer {mentee_jwt}"}
    )

    data = json.loads(response.data.decode())
    assert response.status_code == HTTPStatus.OK
    assert data["success"] is True

def test_mentor_send_message(client):
    mentor_jwt = create_jwt_token(DUMMY_MENTOR_ID, 'mentor')
    mentee_jwt = create_jwt_token(DUMMY_MENTEE_ID, 'mentee')

    response = client.post(
        "/chats/mentor/send-message",
        data=json.dumps({"recipient_id": DUMMY_MENTEE_ID, "content": "Hello, mentee!"}),
        content_type="application/json",
        headers={"Authorization": f"Bearer {mentor_jwt}"}
    )

    data = json.loads(response.data.decode())
    assert response.status_code == HTTPStatus.OK
    assert data["message"] == "Message sent successfully."

def test_mentee_send_message(client):
    mentee_jwt = create_jwt_token(DUMMY_MENTEE_ID, 'mentee')
    mentor_jwt = create_jwt_token(DUMMY_MENTOR_ID, 'mentor')

    response = client.post(
        "/chats/mentee/send-message",
        data=json.dumps({"recipient_id": DUMMY_MENTOR_ID, "content": "Hello, mentor!"}),
        content_type="application/json",
        headers={"Authorization": f"Bearer {mentee_jwt}"}
    )

    data = json.loads(response.data.decode())
    assert response.status_code == HTTPStatus.OK
    assert data["message"] == "Message sent successfully."

def test_mentor_post_in_community(client):
    mentor_jwt = create_jwt_token(DUMMY_MENTOR_ID, 'mentor')

    response = client.post(
        "/chats/community/mentor/post",
        data=json.dumps({"community_id": DUMMY_COMMUNITY_ID, "content": "Hello, community!"}),
        content_type="application/json",
        headers={"Authorization": f"Bearer {mentor_jwt}"}
    )

    data = json.loads(response.data.decode())
    assert response.status_code == HTTPStatus.OK
    assert data["message"] == "Message posted in community successfully."

def test_mentee_post_in_community(client):
    mentee_jwt = create_jwt_token(DUMMY_MENTEE_ID, 'mentee')

    response = client.post(
        "/chats/community/mentee/post",
        data=json.dumps({"community_id": DUMMY_COMMUNITY_ID, "content": "Hello, community!"}),
        content_type="application/json",
        headers={"Authorization": f"Bearer {mentee_jwt}"}
    )

    data = json.loads(response.data.decode())
    assert response.status_code == HTTPStatus.OK
    assert data["message"] == "Message posted in community successfully."

def test_get_all_messages(client):
    mentee_jwt = create_jwt_token(DUMMY_MENTEE_ID, 'mentee')

    response = client.get(
        "/chats/messages",
        content_type="application/json",
        headers={"Authorization": f"Bearer {mentee_jwt}"}
    )

    data = json.loads(response.data.decode())
    assert response.status_code == HTTPStatus.OK
    assert "messages" in data
    assert isinstance(data["messages"], list)

def test_get_all_community_messages(client):
    mentor_jwt = create_jwt_token(DUMMY_MENTOR_ID, 'mentor')

    response = client.get(
        "/chats/community/messages",
        content_type="application/json",
        headers={"Authorization": f"Bearer {mentor_jwt}"}
    )

    data = json.loads(response.data.decode())
    assert response.status_code == HTTPStatus.OK
    assert isinstance(data, list)
