import pytest
from unittest.mock import AsyncMock, patch
from fastapi import HTTPException

from app.users.service import UserService
from app.users.model import UserRegisterResponse, TokenResponse



# Fixtures
@pytest.fixture
def mock_dao():
    return AsyncMock()


@pytest.fixture
def user_service(mock_dao):
    return UserService(dao=mock_dao)


# Register user tests
@pytest.mark.asyncio
@patch(
    "app.users.service.validate_password_strength",
    side_effect=ValueError("Password is too short!")
)
async def test_register_user_with_weak_password_deny(_, user_service):
    with pytest.raises(HTTPException) as exc:
        await user_service.register_user(
            email="developer@example.com",
            password="123",
            phone="07120004231",
            username="dev",
        )

    assert exc.value.status_code == 400
    assert exc.value.detail == "Password is too short!"


@pytest.mark.asyncio
async def test_register_existing_user(user_service):
    user_service.dao.get_by_email_and_username.return_value = object()

    with pytest.raises(HTTPException) as exc:
        await user_service.register_user(
            email="dev@example.com",
            username="developerone",
            password="StrongPasswordThisTime432!",
            phone="07120004231",
        )

    assert exc.value.status_code == 400
    assert "already exists" in exc.value.detail


@pytest.mark.asyncio
@patch("app.users.service.validate_password_strength", return_value=None)
@patch("app.users.service.hash_password", return_value="hashed")
async def test_register_user_success(_, __, user_service):
    user_service.dao.get_by_email_and_username.return_value = None
    user_service.dao.create_user.return_value = "userobj001"

    result = await user_service.register_user(
        email="developer@example.com",
        password="AstrongPasswordThisOther124!",
        phone="07120004231",
        username="dev",
    )

    assert isinstance(result, UserRegisterResponse)
    assert result.user_id == "userobj001"
    assert "successfully registered" in result.message


# Login tests
@pytest.mark.asyncio
async def test_login_with_invalid_credentials(user_service):
    user_service.dao.get_by_email.return_value = None

    with pytest.raises(HTTPException) as exc:
        await user_service.user_login(
            email="dev@example.com",
            password="wrongpassword",
        )

    assert exc.value.status_code == 401


@pytest.mark.asyncio
@patch("app.users.service.verify_password", return_value=True)
@patch("app.auth.jwt.create_access_token", return_value="jwt-token")
async def test_login_success(_, __, user_service):
    user_service.dao.get_by_email.return_value = type(
        "User", (), {"id": "user001", "password": "hashed"}
    )()

    result = await user_service.user_login(
        email="dev@example.com",
        password="correctpassword",
    )

    assert isinstance(result, TokenResponse)
    assert result.access_token == "jwt-token"
