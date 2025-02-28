import asyncio
from asyncio.log import logger
import logging

from server.services.service import singleton
from server.db.mongo_client import mongo_client


@singleton
class SessionService:
    def set(self, peer_id: str, user_id: str) -> None:
        logging.info(f"Setting session for {peer_id} to {user_id}")
        mongo_client.db.sessions.update_one(
            {"peer_id": peer_id}, {"$set": {"user_id": user_id}}, upsert=True
        )

    def get_client_id(self, peer_id: str | None) -> str | None:
        if peer_id is None:
            return None
        session = mongo_client.db.sessions.find_one({"peer_id": peer_id})
        return session["user_id"] if session else None

    def delete(self, peer_id: str | None) -> None:
        if peer_id is not None:
            mongo_client.db.sessions.delete_one({"peer_id": peer_id})
