from app.users.dao import UserDAO
import pytest
from unittest.mock import AsyncMock
from app.users.model import UserDB


@pytest.fixture
def mock_conn():
    return AsyncMock()

@pytest.fixture
def user_dao(mock_conn):
    return UserDAO(mock_conn)

@pytest.mark.asyncio
async def test_create_user(user_dao, mock_conn):
    mock_conn.fetchrow.return_value = {"id": "userX24"}

    user_id = await user_dao.create_user(
        user_id="userX24",
        username="developer",
        email="developer@example.com",
        phone="0783434834",
        hashed_password="hashed",
        role="user"
    )

    mock_conn.fetchrow.assert_awaited_once()
    assert user_id == "userX24"

@pytest.mark.asyncio
async def test_get_by_email_found(user_dao, mock_conn):
    row = {
        "id": "user01",
        "username": "dev",
        "email": "dev@example.com",
    }
    mock_conn.fetchrow.return_value = row

    result = await user_dao.get_by_email("dev@example.com")
    mock_conn.fetchrow.assert_awaited_once()
    assert isinstance(result, UserDB)
    assert result.id == "user01"
    assert result.username == "dev"

@pytest.mark.asyncio
async def test_get_by_email_not_found(user_dao, mock_conn):
    mock_conn.fetchrow.return_value = None
    result = await user_dao.get_by_email("missinguser@example.com")
    assert result is None

@pytest.mark.asyncio
async def test_get_by_id_found(user_dao, mock_conn):
    row = {
        "id": "user02",
        "username": "anotherdev",
        "email": "anotherdev@example.com"
    }

    mock_conn.fetchrow.return_value = row

    result = await user_dao.get_by_id("user02")
    mock_conn.fetchrow.assert_awaited_once()
    assert isinstance(result, UserDB)
    assert result.username == "anotherdev"
    assert result.email == "anotherdev@example.com"

@pytest.mark.asyncio
async def test_get_by_id_not_found(user_dao, mock_conn):
    mock_conn.fetchrow.return_value = None
    result = await user_dao.get_by_id("missingdev")
    assert result is None

@pytest.mark.asyncio
async def test_get_by_email_and_username_found(user_dao, mock_conn):
    row = {
        "id": "user03",
        "username": "andanotherdev",
        "email": "another@example.com",
        "phone": "0783434834",
        "role": "user"
    }

    mock_conn.fetchrow.return_value = row

    result = await user_dao.get_by_email_and_username("andanotherdev", "andanotherdev")

    mock_conn.fetchrow.assert_awaited_once()
    assert isinstance(result, UserDB)
    assert result.id == "user03"
    assert result.email == "another@example.com"
    assert result.username == "andanotherdev"
    assert result.phone == "0783434834"
    assert result.role == "user"

@pytest.mark.asyncio
async def test_get_by_email_and_username_not_found(user_dao, mock_conn):
    mock_conn.fetchrow.return_value = None
    result = await user_dao.get_by_email_and_username("andanotherdev", "missinguser")
    assert result is None
