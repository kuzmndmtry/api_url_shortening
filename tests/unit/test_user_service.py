from fastapi import HTTPException
import pytest
from app.db.models.user import User
from app.services.user_service import create_user
from tests.test_data import  PASSWORD, USERNAME


@pytest.fixture
def mock_db(mocker):
    db = mocker.Mock()
    query_mock = mocker.Mock()
    filter_mock = mocker.Mock()
    filter_mock.first.return_value = None
    query_mock.filter.return_value = filter_mock
    db.query.return_value = query_mock
    return db

def test_create_user(mock_db):
    user = create_user(mock_db, USERNAME, PASSWORD)
    assert user.username == USERNAME
    assert user.password == PASSWORD

def test_create_user_existing_username(mock_db):
    mock_db.query().filter().first.return_value = User(username=USERNAME, password=PASSWORD)
    with pytest.raises(HTTPException) as exc_info:
        create_user(mock_db, USERNAME, PASSWORD)
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Username already registered"

