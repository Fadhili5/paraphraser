import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from app.users.route import router
from app.db.connection import get_pool
from app.users.model import UserRegisterResponse, TokenResponse

@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(router)

    async def fake_pool():
        return AsyncMock()

    app.dependency_overrides[get_pool] = fake_pool

    return TestClient(app)


@patch("app.users.route.UserService.register_user")
def test_register_user_success(mock_register, client):
    mock_register.return_value = UserRegisterResponse(
        message="User Account Successfully Created",
        user_id="user001"
    )

    payload = {
        "email": "dev@example.com",
        "username": "dev",
        "password": "StrongPassword",
        "phone": "070054232423"
    }

    response = client.post("/v1/users/register", json=payload)

    assert response.status_code == 201
    assert response.json()["user_id"] == "user001"


@patch("app.users.route.UserService")
def test_register_user_existing_user(mock_service, client):
    service_instance = mock_service.return_value
    service_instance.register_user.side_effect = HTTPException(
        status_code=400,
        detail="already exists"
    )

    payload = {
        "email": "dev@example.com",
        "username": "dev",
        "password": "StrongPassword1",
        "phone": "070054232423"
    }

    response = client.post("/v1/users/register", json=payload)

    assert response.status_code == 400
    assert "already exists" == response.json()["detail"]

@patch("app.users.route.UserService")
def test_login_success(mock_service, client):
    service_instance = mock_service.return_value
    service_instance.user_login = AsyncMock(
        return_value=TokenResponse(access_token="jwt-token")
    )

    payload = {
        "email": "dev@example.com",
        "password": "CorrectStrongPassword1",
    }

    response = client.post("/v1/users/login", json=payload)

    assert response.status_code == 200


@patch("app.users.route.UserService")
def test_login_invalid_credentials(mock_service, client):
    service_instance = mock_service.return_value
    service_instance.user_login.side_effect = HTTPException(
        status_code=400,
        detail="Invalid Credentials"
    )

    payload = {
        "email": "dev@example.com",
        "password": "WrongStrongPassword1"
    }
    response = client.post("/v1/users/login", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid Credentials"