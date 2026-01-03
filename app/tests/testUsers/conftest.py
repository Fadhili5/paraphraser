import pytest
from unittest.mock import AsyncMock
from app.users.service import UserService

@pytest.fixture
def mock_dao():
    return AsyncMock()

@pytest.fixture
def user_service(mock_dao):
    return UserService(dao=mock_dao())