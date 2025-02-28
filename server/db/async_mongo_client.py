import sys
from typing import Any

from mongomock_motor import AsyncMongoMockClient, AsyncMongoMockDatabase  # type: ignore
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from server.services.service import singleton


@singleton
class AsyncMongoClient:
    def __init__(self) -> None:
        self.client: (
            AsyncMongoMockClient[dict[str, Any]] | AsyncIOMotorClient[dict[str, Any]]
        )
        if "pytest" in sys.modules:
            self.client = AsyncMongoMockClient()
        else:
            self.client = AsyncIOMotorClient("mongodb://localhost:27017")
        self.db: AsyncIOMotorDatabase[dict[str, Any]] | AsyncMongoMockDatabase[dict[str, Any]] = self.client.synthesia_db


    def close(self) -> None:
        """Close the MongoDB connection"""
        self.client.close()


# Global instance
async_mongo_client = AsyncMongoClient()
