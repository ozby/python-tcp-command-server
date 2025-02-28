import sys
from typing import Any

import mongomock
import pymongo
from pymongo.database import Database

from server.services.service import singleton


@singleton
class MongoClient:
    def __init__(self) -> None:
        self.client: (
            mongomock.MongoClient[dict[str, Any]] | pymongo.MongoClient[dict[str, Any]]
        )
        if "pytest" in sys.modules:
            self.client = mongomock.MongoClient()
        else:
            self.client = pymongo.MongoClient(
                "mongodb://admin:password@localhost:27017/admin"
            )
        self.db: Database[dict[str, Any]] = self.client.synthesia_db

    @property
    def database(self) -> Database[dict[str, Any]]:
        return self.db

    def close(self) -> None:
        """Close the MongoDB connection"""
        self.client.close()


# Global instance
mongo_client = MongoClient()
