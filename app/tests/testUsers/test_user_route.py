import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from app.users.route import router
from app.users.model import UserRegisterResponse, TokenResponse
from app.db.connection import get_pool


class FakeConn:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass


class FakePool:
    def acquire(self):
        return FakeConn()


@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(router)

    app.dependency_overrides[get_pool] = lambda: FakePool()
    return TestClient(app)


# User Registration
@patch("app.users.route.guard_captcha", return_value=None)
@patch("app.users.route.UserService")
def test_register_user_success(mock_service, _, client):
    user_id = uuid4()

    service_instance = mock_service.return_value
    service_instance.register_user = AsyncMock(
        return_value=UserRegisterResponse(
            message="User account successfully created",
            user_id=user_id
        )
    )

    payload = {
        "email": "dev@example.com",
        "username": "dev",
        "password": "StrongPassword123!",
        "phone_number": "070054232423",
        "recaptcha_token": "fake"
    }

    response = client.post("/v1/users/register", json=payload)

    assert response.status_code == 201
    assert response.json()["user_id"] == str(user_id)


@patch("app.users.route.guard_captcha", return_value=None)
@patch("app.users.route.UserService")
def test_register_user_existing_user(mock_service, _, client):
    service_instance = mock_service.return_value
    service_instance.register_user = AsyncMock(
        side_effect=HTTPException(
            status_code=400,
            detail="User already exists"
        )
    )

    payload = {
        "email": "dev@example.com",
        "username": "dev",
        "password": "StrongPassword123!",
        "phone_number": "070054232423",
        "recaptcha_token": "fake"
    }

    response = client.post("/v1/users/register", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "User already exists"

# User Login
@patch("app.users.route.guard_captcha", return_value=None)
@patch("app.users.route.UserService")
def test_login_success(mock_service, _, client):
    service_instance = mock_service.return_value
    service_instance.user_login = AsyncMock(
        return_value=TokenResponse(access_token="jwt-token")
    )

    payload = {
        "email": "dev@example.com",
        "password": "CorrectStrongPassword123!",
        "recaptcha_token": "fake"
    }

    response = client.post("/v1/users/login", json=payload)

    assert response.status_code == 200
    assert response.json()["access_token"] == "jwt-token"


@patch("app.users.route.guard_captcha", return_value=None)
@patch("app.users.route.UserService")
def test_login_invalid_credentials(mock_service, _, client):
    service_instance = mock_service.return_value
    service_instance.user_login = AsyncMock(
        side_effect=HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )
    )

    payload = {
        "email": "dev@example.com",
        "password": "WrongPassword123!",
        "recaptcha_token": "fake"
    }

    response = client.post("/v1/users/login", json=payload)

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"
