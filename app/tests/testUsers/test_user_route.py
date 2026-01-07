import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from app.users.route import router
from app.users.model import UserRegisterResponse, TokenResponse
from app.db.connection import get_pool


@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(router)

    async def fake_pool():
        return AsyncMock()

    app.dependency_overrides[get_pool] = fake_pool
    return TestClient(app)


@patch("app.users.route.guard_captcha", return_value=None)
@patch("app.users.route.UserService")
def test_register_user_success(mock_service, _, client):
    service_instance = mock_service.return_value
    service_instance.register_user = AsyncMock(
        return_value=UserRegisterResponse(
            message="User Account successfully created!",
            user_id="user001"
        )
    )

    payload = {
        "email": "dev@example.com",
        "username": "dev",
        "password": "StrongPassword",
        "phone": "070054232423",
        "recaptcha_token": "fake"
    }

    response = client.post("/v1/users/register", json=payload)

    assert response.status_code == 201
    assert response.json()["user_id"] == "user001"


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
        "password": "StrongPassword1",
        "phone": "070054232423",
        "recaptcha_token": "fake"
    }

    response = client.post("/v1/users/register", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "User already exists"


@patch("app.users.route.guard_captcha", return_value=None)
@patch("app.users.route.UserService")
def test_login_success(mock_service, _, client):
    service_instance = mock_service.return_value
    service_instance.user_login = AsyncMock(
        return_value=TokenResponse(access_token="jwt-token")
    )

    payload = {
        "email": "dev@example.com",
        "password": "CorrectStrongPassword1",
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
        "password": "WrongPassword",
        "recaptcha_token": "fake"
    }

    response = client.post("/v1/users/login", json=payload)

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"
