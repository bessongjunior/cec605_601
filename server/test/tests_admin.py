import pytest
import json
from http import HTTPStatus
from your_flask_app import app  # replace 'your_flask_app' with the actual name of your Flask app module
from flask_jwt_extended import create_access_token
from flask_socketio import SocketIO

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
