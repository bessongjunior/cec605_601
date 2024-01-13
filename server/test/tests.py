



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






DUMMY_MENTOR_EMAIL = "mentor@example.com"
DUMMY_MENTEE_EMAIL = "mentee@example.com"
DUMMY_COMMUNITY_ID = 1

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

@pytest.fixture
def socketio():
    return SocketIO(app)

def create_jwt_token(email):
    identity = {'email': email}
    token = create_access_token(identity=identity)
    return token

def test_webrtc_test_endpoint(client):
    response = client.get("/webrtc/test")
    data = json.loads(response.data.decode())
    assert response.status_code == HTTPStatus.OK
    assert data["success"] is True

def test_webrtc_connect_and_disconnect(socketio):
    client_socket = socketio.test_client()

    # Test connect
    client_socket.emit('connect', namespace='/webrtc_ns')
    received_connect = client_socket.get_received(namespace='/webrtc_ns')
    assert received_connect[0]['name'] == 'connect'

    # Test disconnect
    client_socket.disconnect(namespace='/webrtc_ns')
    received_disconnect = client_socket.get_received(namespace='/webrtc_ns')
    assert received_disconnect[0]['name'] == 'disconnect'

def test_webrtc_call_student_mentor(socketio):
    mentor_jwt = create_jwt_token(DUMMY_MENTOR_EMAIL)
    mentee_jwt = create_jwt_token(DUMMY_MENTEE_EMAIL)

    mentor_socket = socketio.test_client()
    mentor_socket.connect(namespace='/webrtc_ns', headers={"Authorization": f"Bearer {mentor_jwt}"})

    mentee_socket = socketio.test_client()
    mentee_socket.connect(namespace='/webrtc_ns', headers={"Authorization": f"Bearer {mentee_jwt}"})

    # Test call
    mentor_socket.emit('call-student-mentor', {'other_user_id': mentee_socket.sid}, namespace='/webrtc_ns')
    received_call = mentor_socket.get_received(namespace='/webrtc_ns')
    assert received_call[0]['name'] == 'incoming-call'

    # Test answer call
    mentee_socket.emit('answer-call', {'accept': True}, namespace='/webrtc_ns')
    received_answer = mentee_socket.get_received(namespace='/webrtc_ns')
    assert received_answer[0]['name'] == 'call-accepted'

    mentor_socket.disconnect(namespace='/webrtc_ns')
    mentee_socket.disconnect(namespace='/webrtc_ns')

def test_webrtc_call_community(socketio):
    mentor_jwt = create_jwt_token(DUMMY_MENTOR_EMAIL)

    mentor_socket = socketio.test_client()
    mentor_socket.connect(namespace='/webrtc_ns', headers={"Authorization": f"Bearer {mentor_jwt}"})

    # Test call
    mentor_socket.emit('call-community', {'community_id': DUMMY_COMMUNITY_ID}, namespace='/webrtc_ns')
    received_call = mentor_socket.get_received(namespace='/webrtc_ns')
    assert received_call[0]['name'] == 'incoming-community-call'

    mentor_socket.disconnect(namespace='/webrtc_ns')





@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

@pytest.fixture
def socketio():
    return SocketIO(app)

def create_jwt_token(email):
    identity = {'email': email}
    token = create_access_token(identity=identity)
    return token

def test_webrtc_test_endpoint(client):
    response = client.get("/webrtc/test")
    data = json.loads(response.data.decode())
    assert response.status_code == HTTPStatus.OK
    assert data["success"] is True

def test_webrtc_connect_and_disconnect(socketio):
    client_socket = socketio.test_client()

    # Test connect
    client_socket.emit('connect', namespace='/webrtc_ns')
    received_connect = client_socket.get_received(namespace='/webrtc_ns')
    assert received_connect[0]['name'] == 'connect'

    # Test disconnect
    client_socket.disconnect(namespace='/webrtc_ns')
    received_disconnect = client_socket.get_received(namespace='/webrtc_ns')
    assert received_disconnect[0]['name'] == 'disconnect'

def test_webrtc_call_student_mentor(socketio):
    mentor_jwt = create_jwt_token(DUMMY_MENTOR_EMAIL)
    mentee_jwt = create_jwt_token(DUMMY_MENTEE_EMAIL)

    mentor_socket = socketio.test_client()
    mentor_socket.connect(namespace='/webrtc_ns', headers={"Authorization": f"Bearer {mentor_jwt}"})

    mentee_socket = socketio.test_client()
    mentee_socket.connect(namespace='/webrtc_ns', headers={"Authorization": f"Bearer {mentee_jwt}"})

    # Test call
    mentor_socket.emit('call-student-mentor', {'other_user_id': mentee_socket.sid}, namespace='/webrtc_ns')
    received_call = mentor_socket.get_received(namespace='/webrtc_ns')
    assert received_call[0]['name'] == 'incoming-call'

    # Test answer call
    mentee_socket.emit('answer-call', {'accept': True}, namespace='/webrtc_ns')
    received_answer = mentee_socket.get_received(namespace='/webrtc_ns')
    assert received_answer[0]['name'] == 'call-accepted'

    mentor_socket.disconnect(namespace='/webrtc_ns')
    mentee_socket.disconnect(namespace='/webrtc_ns')

def test_webrtc_call_community(socketio):
    mentor_jwt = create_jwt_token(DUMMY_MENTOR_EMAIL)

    mentor_socket = socketio.test_client()
    mentor_socket.connect(namespace='/webrtc_ns', headers={"Authorization": f"Bearer {mentor_jwt}"})

    # Test call
    mentor_socket.emit('call-community', {'community_id': DUMMY_COMMUNITY_ID}, namespace='/webrtc_ns')
    received_call = mentor_socket.get_received(namespace='/webrtc_ns')
    assert received_call[0]['name'] == 'incoming-community-call'

    mentor_socket.disconnect(namespace='/webrtc_ns')



DUMMY_MENTOR_EMAIL = "mentor@example.com"
DUMMY_PASSWORD = "password123"

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

@pytest.fixture
def socketio():
    return SocketIO(app)

def create_jwt_token(email):
    identity = {'email': email}
    token = create_access_token(identity=identity)
    return token

def test_mentor_register(client):
    response = client.post(
        "/mentor/v1/auth/signup",
        json={
            "username": "mentor1",
            "fullname": "Mentor One",
            "matricule": "MAT123",
            "email": DUMMY_MENTOR_EMAIL,
            "password": DUMMY_PASSWORD,
            "department": "Computer Science",
        },
    )
    data = json.loads(response.data.decode())
    assert response.status_code == HTTPStatus.CREATED
    assert data["success"] is True

def test_mentor_login(client):
    client.post(
        "/mentor/v1/auth/signup",
        json={
            "username": "mentor1",
            "fullname": "Mentor One",
            "matricule": "MAT123",
            "email": DUMMY_MENTOR_EMAIL,
            "password": DUMMY_PASSWORD,
            "department": "Computer Science",
        },
    )

    response = client.post(
        "/mentor/v1/auth/signin",
        json={"email": DUMMY_MENTOR_EMAIL, "password": DUMMY_PASSWORD},
    )
    data = json.loads(response.data.decode())
    assert response.status_code == HTTPStatus.CREATED
    assert data["success"] is True
    assert "token" in data

def test_mentor_edit_details(client):
    token = create_jwt_token(DUMMY_MENTOR_EMAIL)
    headers = {"Authorization": f"Bearer {token}"}

    response = client.patch(
        "/mentor/v1/mentor/edit",
        json={"username": "newusername", "email": "newemail@example.com"},
        headers=headers,
    )
    data = json.loads(response.data.decode())
    assert response.status_code == HTTPStatus.ACCEPTED
    assert data["success"] is True
    # Add more assertions based on your expected changes

def test_mentor_upload_profile_picture(client):
    token = create_jwt_token(DUMMY_MENTOR_EMAIL)
    headers = {"Authorization": f"Bearer {token}"}

    with open("path/to/test/image.jpg", "rb") as img_file:
        response = client.put(
            "/mentor/v1/mentor/edit",
            headers=headers,
            data={"profile_picture": (img_file, "image.jpg")},
        )
        data = json.loads(response.data.decode())
        assert response.status_code == HTTPStatus.ACCEPTED
        assert data["success"] is True

def test_mentor_logout(client):
    token = create_jwt_token(DUMMY_MENTOR_EMAIL)
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post("/mentor/v1/auth/logout", headers=headers)
    data = json.loads(response.data.decode())
    assert response.status_code == HTTPStatus.OK
    assert data["success"] is True




DUMMY_MENTEE_EMAIL = "mentee@example.com"
DUMMY_PASSWORD = "password123"

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

@pytest.fixture
def socketio():
    return SocketIO(app)

def create_jwt_token(email):
    identity = {'email': email}
    token = create_access_token(identity=identity)
    return token

def test_mentee_register(client):
    response = client.post(
        "/mentee/v1/auth/register",
        json={
            "username": "mentee1",
            "fullname": "Mentee One",
            "matricule": "MAT123",
            "email": DUMMY_MENTEE_EMAIL,
            "password": DUMMY_PASSWORD,
            "department": "Computer Science",
        },
    )
    data = json.loads(response.data.decode())
    assert response.status_code == HTTPStatus.CREATED
    assert data["success"] is True

def test_mentee_login(client):
    client.post(
        "/mentee/v1/auth/register",
        json={
            "username": "mentee1",
            "fullname": "Mentee One",
            "matricule": "MAT123",
            "email": DUMMY_MENTEE_EMAIL,
            "password": DUMMY_PASSWORD,
            "department": "Computer Science",
        },
    )

    response = client.post(
        "/mentee/v1/auth/login",
        json={"email": DUMMY_MENTEE_EMAIL, "password": DUMMY_PASSWORD},
    )
    data = json.loads(response.data.decode())
    assert response.status_code == HTTPStatus.CREATED
    assert data["success"] is True
    assert "token" in data

def test_mentee_edit_details(client):
    token = create_jwt_token(DUMMY_MENTEE_EMAIL)
    headers = {"Authorization": f"Bearer {token}"}

    response = client.patch(
        "/mentee/v1/mentee/edit",
        json={"username": "newusername", "email": "newemail@example.com"},
        headers=headers,
    )
    data = json.loads(response.data.decode())
    assert response.status_code == HTTPStatus.ACCEPTED
    assert data["success"] is True
    # Add more assertions based on your expected changes

def test_mentee_upload_profile_picture(client):
    token = create_jwt_token(DUMMY_MENTEE_EMAIL)
    headers = {"Authorization": f"Bearer {token}"}

    with open("path/to/test/image.jpg", "rb") as img_file:
        response = client.put(
            "/mentee/v1/mentee/edit",
            headers=headers,
            data={"profile_picture": (img_file, "image.jpg")},
        )
        data = json.loads(response.data.decode())
        assert response.status_code == HTTPStatus.ACCEPTED
        assert data["success"] is True

def test_mentee_logout(client):
    token = create_jwt_token(DUMMY_MENTEE_EMAIL)
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post("/mentee/v1/auth/logout", headers=headers)
    data = json.loads(response.data.decode())
    assert response.status_code == HTTPStatus.OK
    assert data["success"] is True




@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

@pytest.fixture
def socketio():
    return SocketIO(app)

def create_jwt_token(email):
    identity = {'email': email}
    token = create_access_token(identity=identity)
    return token

def test_mentee_register(client):
    response = client.post(
        "/mentee/v1/auth/register",
        json={
            "username": "mentee1",
            "fullname": "Mentee One",
            "matricule": "MAT123",
            "email": DUMMY_MENTEE_EMAIL,
            "password": DUMMY_PASSWORD,
            "department": "Computer Science",
        },
    )
    data = json.loads(response.data.decode())
    assert response.status_code == HTTPStatus.CREATED
    assert data["success"] is True

def test_mentee_login(client):
    client.post(
        "/mentee/v1/auth/register",
        json={
            "username": "mentee1",
            "fullname": "Mentee One",
            "matricule": "MAT123",
            "email": DUMMY_MENTEE_EMAIL,
            "password": DUMMY_PASSWORD,
            "department": "Computer Science",
        },
    )

    response = client.post(
        "/mentee/v1/auth/login",
        json={"email": DUMMY_MENTEE_EMAIL, "password": DUMMY_PASSWORD},
    )
    data = json.loads(response.data.decode())
    assert response.status_code == HTTPStatus.CREATED
    assert data["success"] is True
    assert "token" in data

def test_mentee_edit_details(client):
    token = create_jwt_token(DUMMY_MENTEE_EMAIL)
    headers = {"Authorization": f"Bearer {token}"}

    response = client.patch(
        "/mentee/v1/mentee/edit",
        json={"username": "newusername", "email": "newemail@example.com"},
        headers=headers,
    )
    data = json.loads(response.data.decode())
    assert response.status_code == HTTPStatus.ACCEPTED
    assert data["success"] is True
    # Add more assertions based on your expected changes

def test_mentee_upload_profile_picture(client):
    token = create_jwt_token(DUMMY_MENTEE_EMAIL)
    headers = {"Authorization": f"Bearer {token}"}

    with open("path/to/test/image.jpg", "rb") as img_file:
        response = client.put(
            "/mentee/v1/mentee/edit",
            headers=headers,
            data={"profile_picture": (img_file, "image.jpg")},
        )
        data = json.loads(response.data.decode())
        assert response.status_code == HTTPStatus.ACCEPTED
        assert data["success"] is True

def test_mentee_logout(client):
    token = create_jwt_token(DUMMY_MENTEE_EMAIL)
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post("/mentee/v1/auth/logout", headers=headers)
    data = json.loads(response.data.decode())
    assert response.status_code == HTTPStatus.OK
    assert data["success"] is True
import json
import pytest
from flask import Flask
from flask.testing import FlaskClient
from http import HTTPStatus
from your_flask_app import app  # replace 'your_flask_app' with the actual name of your Flask app module
from flask_jwt_extended import create_access_token
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask.testing import FlaskClient

DUMMY_MENTEE_EMAIL = "mentee@example.com"
DUMMY_MENTEE_PASSWORD = "password123"

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

@pytest.fixture
def socketio():
    return SocketIO(app)

def create_jwt_token(email):
    identity = {'email': email}
    token = create_access_token(identity=identity)
    return token

def test_get_task_list(client):
    # Assuming there are tasks in the database
    token = create_jwt_token(DUMMY_MENTEE_EMAIL)
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/task/", headers=headers)
    data = json.loads(response.data.decode())
    assert response.status_code == HTTPStatus.OK
    assert isinstance(data, list)

def test_create_task(client):
    token = create_jwt_token(DUMMY_MENTEE_EMAIL)
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post(
        "/task/",
        json={"content": "New task content", "status": "Pending"},
        headers=headers,
    )
    data = json.loads(response.data.decode())
    assert response.status_code == HTTPStatus.CREATED
    assert data["success"] is True
    assert "id" in data

def test_update_task(client):
    # Assuming there is a task in the database
    token = create_jwt_token(DUMMY_MENTEE_EMAIL)
    headers = {"Authorization": f"Bearer {token}"}

    response = client.put(
        "/task/update/1",
        json={"content": "Updated task content", "status": "Completed"},
        headers=headers,
    )
    data = json.loads(response.data.decode())
    assert response.status_code == HTTPStatus.CREATED
    assert data["success"] is True
    assert data["id"] == 1

def test_delete_task(client):
    # Assuming there is a task in the database
    token = create_jwt_token(DUMMY_MENTEE_EMAIL)
    headers = {"Authorization": f"Bearer {token}"}

    response = client.delete("/task/delete/1", headers=headers)
    assert response.status_code == HTTPStatus.NO_CONTENT


