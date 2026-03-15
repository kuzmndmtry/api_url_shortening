from httpx import AsyncClient
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.api.routes.links import get_db
from app.db.models.link import Link
from app.db.models.user import User  
from tests.test_data import ALIAS, ORIGINAL_URL,ORIGINAL_URL_FAKE


@pytest.mark.asyncio
async  def test_create_link_with_owner(async_client: AsyncClient, fake_db, mock_redis):
    response = await  async_client.post(
        "/links/shorten",
        json={"original_url": ORIGINAL_URL, "custom_alias": ALIAS},
        headers={"User-ID": "1"}  
    )
    assert response.status_code == 200
    data = response.json()
    assert "short_code" in data
    fake_db.clear()

@pytest.mark.asyncio
async def test_create_link_with_nonexistent_owner(async_client: AsyncClient, fake_db, mock_redis, mocker):
    response = await async_client.post(
        "/links/shorten",
        json={"original_url": ORIGINAL_URL, "custom_alias": "otheralias"},
        headers={"User-ID": "999"}  
    )
    assert response.status_code == 401
    fake_db.clear()

@pytest.mark.asyncio
async def test_create_link_without_alias_and_owner(async_client: AsyncClient, fake_db, mock_redis, mocker):
    response = await async_client.post("/links/shorten", json={"original_url": ORIGINAL_URL})

    assert response.status_code == 200
    data = response.json()
    assert data["short_code"]
    fake_db.clear()

@pytest.mark.asyncio
async def test_crate_link_with_alias(async_client: AsyncClient, fake_db, mock_redis, mocker):
    response = await async_client.post("/links/shorten", json={"original_url": ORIGINAL_URL, "custom_alias": ALIAS})

    assert response.status_code == 200
    data = response.json()
    assert data["short_code"]
    fake_db.clear()

@pytest.mark.asyncio
async def test_create_link_with_existing_alias(async_client: AsyncClient, fake_db, mock_redis, mocker):
    link = Link(
        original_url=ORIGINAL_URL,
        short_code=ALIAS,
        owner_id=1
    )
    fake_db.links.append(link)

    response = await async_client.post("/links/shorten", json={"original_url": ORIGINAL_URL, "custom_alias": ALIAS})
    assert response.status_code == 400
    assert response.json() == {"detail": "alias alredy exists"}
    fake_db.clear()

@pytest.mark.asyncio
async def test_search_links(async_client: AsyncClient, fake_db, mock_redis, mocker):
    link = Link(
        original_url=ORIGINAL_URL,
        short_code=ALIAS,
        owner_id=1
    )
    fake_db.links.append(link)

    response = await async_client.get("/links/search", params={"original_url": ORIGINAL_URL}, headers={"X-User-ID": "1"})
    assert response.status_code == 200
    data = response.json()
    fake_db.clear()

@pytest.mark.asyncio
async def test_search_links_not_found(async_client: AsyncClient, fake_db, mock_redis, mocker):

    response = await async_client.get("/links/search", params={"original_url": ORIGINAL_URL_FAKE}, headers={"X-User-ID": "1"})
    assert response.status_code == 404
    assert response.json() == {"detail": "not found"}
    fake_db.clear()

@pytest.mark.asyncio
async def test_clickl(async_client: AsyncClient, fake_db, mock_redis, mocker):
    link = Link(
        original_url=ORIGINAL_URL,
        short_code=ALIAS,
        owner_id=1,
        count_clicks = 0
    )
    fake_db.links.append(link)
    mock_redis = mocker.Mock()
    mock_redis.get.return_value = None
    mocker.patch("app.api.routes.links.redis", mock_redis)

    response = await async_client.get(f"/links/{ALIAS}")

    assert response.status_code == 200
    data = response.json()
    assert data["original_url"] == ORIGINAL_URL
    assert link.count_clicks == 1
    fake_db.clear()

@pytest.mark.asyncio
async def test_update_links(async_client: AsyncClient, fake_db, mock_redis, mocker):
    link = Link(
        original_url=ORIGINAL_URL,
        short_code=ALIAS,
        owner_id=1,
        count_clicks = 0
    )

    fake_db.links.append(link)
    mock_redis = mocker.Mock()
    mock_redis.get.return_value = None
    mocker.patch("app.api.routes.links.redis", mock_redis)

    response = await async_client.put(f"/links/{ALIAS}", headers={"X-User-ID": "1"})

    assert response.status_code == 200
    data = response.json()
    assert data["short_code"] != ALIAS
    fake_db.clear()

@pytest.mark.asyncio
async def test_delete_links(async_client: AsyncClient, fake_db, mock_redis, mocker):
    link = Link(
        original_url=ORIGINAL_URL,
        short_code=ALIAS,
        owner_id=1,
        count_clicks = 0
    )

    fake_db.links.append(link)
    mock_redis = mocker.Mock()
    mock_redis.get.return_value = None
    mocker.patch("app.api.routes.links.redis", mock_redis)

    response = await async_client.delete(f"/links/{ALIAS}", headers={"X-User-ID": "1"})

    assert response.status_code == 200
    assert link not in fake_db.links
    assert response.json() == {"detail": "success!"}

    fake_db.clear()

@pytest.mark.asyncio
async def test_delete_link_unauthorized(async_client: AsyncClient, fake_db, mock_redis, mocker):
    link = Link(
        original_url=ORIGINAL_URL,
        short_code=ALIAS,
        owner_id=1,
        count_clicks = 0
    )
    fake_db.links.append(link)

    response = await async_client.delete(f"/links/{ALIAS}", headers={"X-User-ID": "2"})

    assert response.status_code == 403
    assert response.json() == {"detail": "access denied"}

    fake_db.clear()

@pytest.mark.asyncio
async def test_delete_link_not_foud(async_client: AsyncClient, fake_db, mock_redis, mocker):

    response = await async_client.delete(f"/links/{ALIAS}", headers={"X-User-ID": "2"})

    assert response.status_code == 404
    assert response.json() == {"detail": "not found"}

    fake_db.clear()

@pytest.mark.asyncio
async def test_get_statistics(async_client: AsyncClient, fake_db, mock_redis, mocker):
    link = Link(
        original_url=ORIGINAL_URL,
        short_code=ALIAS,
        owner_id=1,
        count_clicks = 0
    )
    fake_db.links.append(link)

    response = await async_client.get(f"/links/{ALIAS}/stats")

    assert response.status_code == 200
    assert response.json()

    fake_db.clear()

@pytest.mark.asyncio
async def test_get_statistics_link_not_found(async_client: AsyncClient, fake_db, mock_redis, mocker):

    response = await async_client.get(f"/links/{ALIAS}/stats")

    assert response.status_code == 404
    assert response.json() == {"detail": "not found"}

    fake_db.clear()



