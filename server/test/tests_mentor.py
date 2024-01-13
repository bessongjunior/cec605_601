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
