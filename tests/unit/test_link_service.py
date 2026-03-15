from fastapi import HTTPException
import pytest
from app.db.models.link import Link
from app.services.link_service import generate_short_code, chek_alias, create_short_code, get_statistics, get_link
from tests.test_data import ALIAS, OWNER_ID, ORIGINAL_URL


@pytest.fixture
def mock_db(mocker):
    db = mocker.Mock()
    query_mock = mocker.Mock()
    filter_mock = mocker.Mock()
    filter_mock.first.return_value = None
    query_mock.filter_by.return_value = filter_mock
    db.query.return_value = query_mock
    return db

def test_generate_short_code(mock_db):
    # db = mocker.Mock()
    # query_mock = mocker.Mock()
    # filter_mock = mocker.Mock()
    # filter_mock.first.return_value = None
    # query_mock.filter_by.return_value = filter_mock
    # db.query.return_value = query_mock
    code = generate_short_code(mock_db)
    assert len(code) == 6

def test_chek_alias(mock_db):
    assert chek_alias(mock_db, ALIAS) == False
    mock_db.query().filter_by().first.return_value = True
    assert chek_alias(mock_db, "alias") == True

def test_create_short_code_castom_alias(mock_db):
    short_code = create_short_code(mock_db, ORIGINAL_URL, OWNER_ID, ALIAS)
    assert short_code == ALIAS

def test_create_short_code_random_alias(mock_db):
    short_code = create_short_code(mock_db, ORIGINAL_URL, OWNER_ID)
    assert len(short_code) == 6

def test_create_short_code_alias_exists(mock_db):
    mock_db.query().filter_by().first.return_value = True
    with pytest.raises(HTTPException) as exc_info:
        create_short_code(mock_db, ORIGINAL_URL, OWNER_ID, ALIAS)
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == 'alias alredy exists'

def test_get_statistics(mock_db):
    link = Link(original_url=ORIGINAL_URL, short_code=ALIAS, owner_id=OWNER_ID, expires_at=None)
    mock_db.query().filter_by().first.return_value = link

    result = get_statistics(mock_db, link.short_code)
    assert result["original_url"] == link.original_url

def test_get_statistics_not_found(mock_db):
    mock_db.query().filter_by().first.return_value = None
    result = get_statistics(mock_db, ALIAS)
    assert result is None

def test_get_link(mock_db):
    link = Link(original_url=ORIGINAL_URL, short_code=ALIAS, owner_id=OWNER_ID, expires_at=None)
    mock_db.query().filter().first.return_value = link

    result = get_link(mock_db, link.original_url, link.owner_id)
    assert result["original_url"] == link.original_url
    assert result["short_code"] == link.short_code

def test_get_link_not_found(mock_db):
    mock_db.query().filter().first.return_value = None

    result = get_link(mock_db, ORIGINAL_URL, OWNER_ID)
    assert result is None