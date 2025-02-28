import asyncio
from asyncio.log import logger
import logging
from typing import Optional

from server.services.service import singleton
from server.db.mongo_client import mongo_client
from server.db.entities.session import Session


@singleton
class SessionService:
    def __init__(self):
        self.db = mongo_client.db
        self.sessions = self.db.sessions
        self.sessions.create_index("peer_id", unique=True)

    def set(self, peer_id: str, user_id: str) -> None:
        logging.info(f"Setting session for {peer_id} to {user_id}")
        session_doc = {
            "peer_id": peer_id,
            "user_id": user_id
        }
        self.sessions.update_one(
            {"peer_id": peer_id}, 
            {"$set": session_doc}, 
            upsert=True
        )

    def get_client_id(self, peer_id: str | None) -> str | None:
        if peer_id is None:
            return None
        session_doc = self.sessions.find_one(
            {"peer_id": peer_id},
            {"_id": 0}
        )
        if not session_doc:
            return None
        session = Session(**session_doc)
        return session.user_id

    def get_session(self, peer_id: str | None) -> Optional[Session]:
        if peer_id is None:
            return None
        session_doc = self.sessions.find_one(
            {"peer_id": peer_id},
            {"_id": 0}
        )
        if not session_doc:
            return None
        return Session(**session_doc)

    def delete(self, peer_id: str | None) -> None:
        if peer_id is not None:
            self.sessions.delete_one({"peer_id": peer_id})
