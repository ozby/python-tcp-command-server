import sys
from typing import Union, Any, Dict

import mongomock
import pymongo
from pymongo.database import Database

from server.services.service import singleton


@singleton
class MongoClient:
    def __init__(self) -> None:
        self.client: Union[
            mongomock.MongoClient[Dict[str, Any]], pymongo.MongoClient[Dict[str, Any]]
        ]
        if "pytest" in sys.modules:
            self.client = mongomock.MongoClient()
        else:
            self.client = pymongo.MongoClient(
                "mongodb://admin:password@localhost:27017/admin"
            )
        self.db: Database[Dict[str, Any]] = self.client.synthesia_db

    @property
    def database(self) -> Database[Dict[str, Any]]:
        return self.db

    def close(self) -> None:
        """Close the MongoDB connection"""
        self.client.close()


# Global instance
mongo_client = MongoClient()
