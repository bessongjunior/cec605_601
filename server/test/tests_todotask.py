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
