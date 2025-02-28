import sys
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import pymongo
import mongomock
from server.services.service import singleton


@singleton
class MongoClient:
    def __init__(self):
        if "pytest" in sys.modules:
            self.client = mongomock.MongoClient()
        else:
            self.client = pymongo.MongoClient(
                "mongodb://admin:password@localhost:27017/admin"
            )
        self.db = self.client.synthesia_db

    @property
    def database(self):
        return self.db

    def close(self) -> None:
        """Close the MongoDB connection"""
        self.client.close()


# Global instance
mongo_client = MongoClient()
