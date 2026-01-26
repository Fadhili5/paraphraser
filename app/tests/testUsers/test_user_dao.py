import uuid
import pytest
from unittest.mock import AsyncMock
from app.users.dao import UserDAO
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
        hashed_password="hashed",
        phone="0783434834",
        role="user",
    )

    mock_conn.fetchrow.assert_awaited_once()
    assert user_id == "userX24"


@pytest.mark.asyncio
async def test_get_by_email_found(user_dao, mock_conn):
    row = {
        "id": uuid.uuid4(),
        "username": "dev",
        "email": "dev@example.com",
        "password": "hashed",
        "phone_number": "0783434834",
        "role": "user",
    }
    mock_conn.fetchrow.return_value = row

    result = await user_dao.get_by_email("dev@example.com")

    mock_conn.fetchrow.assert_awaited_once()
    assert isinstance(result, UserDB)
    assert result.username == "dev"
    assert result.email == "dev@example.com"


@pytest.mark.asyncio
async def test_get_by_email_not_found(user_dao, mock_conn):
    mock_conn.fetchrow.return_value = None

    result = await user_dao.get_by_email("missinguser@example.com")

    assert result is None


@pytest.mark.asyncio
async def test_get_by_id_found(user_dao, mock_conn):
    user_id = uuid.uuid4()
    row = {
        "id": user_id,
        "username": "anotherdev",
        "email": "anotherdev@example.com",
        "password": "hashed",
        "phone_number": "0783434834",
        "role": "user",
    }
    mock_conn.fetchrow.return_value = row

    result = await user_dao.get_by_id(user_id)

    mock_conn.fetchrow.assert_awaited_once()
    assert isinstance(result, UserDB)
    assert result.id == user_id
    assert result.username == "anotherdev"


@pytest.mark.asyncio
async def test_get_by_id_not_found(user_dao, mock_conn):
    mock_conn.fetchrow.return_value = None

    result = await user_dao.get_by_id(uuid.uuid4())

    assert result is None


@pytest.mark.asyncio
async def test_get_by_email_and_username_found(user_dao, mock_conn):
    row = {
        "id": uuid.uuid4(),
        "username": "andanotherdev",
        "email": "another@example.com",
        "phone_number": "0783434834",
        "role": "user",
    }
    mock_conn.fetchrow.return_value = row

    result = await user_dao.get_by_email_and_username(
        email="another@example.com",
        username="andanotherdev",
    )

    mock_conn.fetchrow.assert_awaited_once()
    assert isinstance(result, UserDB)
    assert result.username == "andanotherdev"
    assert result.email == "another@example.com"
    assert result.phone_number == "0783434834"
    assert result.role == "user"


@pytest.mark.asyncio
async def test_get_by_email_and_username_not_found(user_dao, mock_conn):
    mock_conn.fetchrow.return_value = None

    result = await user_dao.get_by_email_and_username(
        email="missing@example.com",
        username="missinguser",
    )

    assert result is None
