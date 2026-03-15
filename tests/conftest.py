import httpx
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.api.routes.links import get_db
from app.db.models.user import User
from tests.test_data import ALIAS, ORIGINAL_URL


class FakeDB:
    def __init__(self):
        self.links = []  
        self.users = [User(id=1, username="testuser")]  
        self.model = None
        self._filters = {}  
        self._filtered_results = None

    def clear(self):
        self.links = []
        self.model = None
        self._filters = {}
        self._filtered_results = None

    def query(self, model):
        self.model = model
        self._filters = {}
        return self

    def filter(self, *args, **kwargs):
        self._filters.update(kwargs)
        return self

    def filter_by(self, **kwargs):
        self._filters.update(kwargs)
        return self

    def _apply_filters(self, items):
        if not self._filters:
            return items
        
        result = []
        for item in items:
            match = True
            for key, value in self._filters.items():
                if hasattr(item, key):
                    if getattr(item, key) != value:
                        match = False
                        break
                else:
                    match = False
                    break
            if match:
                result.append(item)
        return result

    def first(self):
        if self.model and self.model.__name__ == "Link":
            filtered = self._apply_filters(self.links)
            return filtered[0] if filtered else None
        elif self.model and self.model.__name__ == "User":
            filtered = self._apply_filters(self.users)
            return filtered[0] if filtered else None
        return None

    def all(self):
        if self.model and self.model.__name__ == "Link":
            self._filtered_results = self._apply_filters(self.links)
            return self._filtered_results
        elif self.model and self.model.__name__ == "User":
            self._filtered_results = self._apply_filters(self.users)
            return self._filtered_results
        return []

    def add(self, obj):
        if obj.__class__.__name__ == "Link":
            if not hasattr(obj, 'id'):
                obj.id = len(self.links) + 1  
            self.links.append(obj)
            print(f"Link added: {obj.original_url}, {obj.short_code}")  

    def commit(self):
        print(f"Commit called. Links in DB: {len(self.links)}")  
        pass

    def refresh(self, obj):
        pass

    def delete(self, obj):
        if obj in self.links:
            self.links.remove(obj)

    def clear(self):
        self.links = []

@pytest.fixture
def fake_db():
    return FakeDB()


@pytest.fixture
async def async_client(fake_db):
    app.dependency_overrides[get_db] = lambda: fake_db
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test"  
    ) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture
def mock_redis(mocker):
    mock = mocker.Mock()
    mock.get.return_value = None
    mocker.patch("app.api.routes.links.redis", mock)
    return mock


