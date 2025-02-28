import pytest

from server.db.mongo_client import mongo_client


@pytest.fixture(autouse=True)
def mock_mongo():
    mongo_client.db.discussions.delete_many({})
    mongo_client.db.notifications.delete_many({})
    mongo_client.db.sessions.delete_many({})
