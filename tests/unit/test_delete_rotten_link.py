import datetime
from unittest.mock import MagicMock, patch
import pytest
import os

os.environ["REDIS_URL"] = "redis://localhost:6379/0"
from app.db.models.link import Link
from tests.test_data import ALIAS, ORIGINAL_URL, OWNER_ID


@pytest.fixture
def mock_db():
    db = MagicMock()
    return db
@pytest.fixture
def mock_redis():
    redis = MagicMock()
    return redis

def test_delete_rotten_links():
    expired_link = Link(
        original_url=ORIGINAL_URL,
        short_code=ALIAS,
        owner_id=OWNER_ID,
        expires_at=datetime.datetime.now() - datetime.timedelta(days=1)
    )

    mock_db = MagicMock()
    mock_db.query().filter().all.return_value = [expired_link]

    mock_redis = MagicMock()

    with patch("app.db.session.SessionLocal", return_value=mock_db), \
         patch("app.core.redis.redis", mock_redis):
        from app.tasks.delete_rotten_links import delete_rotten_links
        delete_rotten_links()

    mock_db.delete.assert_called_once_with(expired_link)
    mock_db.commit.assert_called_once()
    mock_db.close.assert_called_once()
    mock_redis.delete.assert_called_once_with(f"link:{ALIAS}")

# def test_delete_rotten_links_last_click():
#     expired_link = Link(
#         original_url=ORIGINAL_URL,
#         short_code=ALIAS,
#         owner_id=OWNER_ID,
#         date_last_click =datetime.datetime.now() - datetime.timedelta(days=40)
#     )

#     mock_db = MagicMock()
#     mock_db.query().filter().all.return_value = [expired_link]

#     mock_redis = MagicMock()

#     with patch("app.db.session.SessionLocal", return_value=mock_db), \
#          patch("app.core.redis.redis", mock_redis):
#         from app.tasks.delete_rotten_links import delete_rotten_links
#         delete_rotten_links()

#     mock_db.delete.assert_called_once_with(expired_link)
#     mock_db.commit.assert_called_once()
#     mock_db.close.assert_called_once()
#     mock_redis.delete.assert_called_once_with(f"link:{ALIAS}")


def test_delete_rotten_links_no_links():
    mock_db = MagicMock()
    mock_db.query().filter().all.return_value = []

    mock_redis = MagicMock()

    with patch("app.db.session.SessionLocal", return_value=mock_db), \
         patch("app.core.redis.redis", mock_redis):
        from app.tasks.delete_rotten_links import delete_rotten_links
        delete_rotten_links()

    mock_db.delete.assert_not_called()
    mock_db.commit.assert_not_called() 
    # mock_db.close.assert_called_once()
    mock_redis.delete.assert_not_called()








