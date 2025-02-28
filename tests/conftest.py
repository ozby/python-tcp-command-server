import pytest

from server.db.async_mongo_client import async_mongo_client


@pytest.fixture(autouse=True)
async def mock_mongo() -> None:
    await async_mongo_client.db.discussions.delete_many({})
    await async_mongo_client.db.notifications.delete_many({})
    await async_mongo_client.db.sessions.delete_many({})