import logging
from typing import Any, cast

from server.db.entities.session import Session
from motor.motor_asyncio import AsyncIOMotorClient

class SessionService:
    def __init__(self, mongo_client: AsyncIOMotorClient) -> None:
        self.db = mongo_client.synthesia_db
        self.sessions = self.db.sessions

    async def set(self, peer_id: str, user_id: str) -> None:
        logging.info(f"Setting session for {peer_id} to {user_id}")
        await self.sessions.update_one(
            {"peer_id": peer_id}, 
            {"$set": {"peer_id": peer_id, "user_id": user_id}}, 
            upsert=True
        )

    async def get_client_id(self, peer_id: str | None) -> str | None:
        if not peer_id:
            return None
        session_doc = await self.sessions.find_one({"peer_id": peer_id}, {"_id": 0})
        if not session_doc:
            return None
        session = Session(**session_doc)
        return session.user_id

    async def get_by_user_id(self, user_id: str | None) -> str | None:
        if not user_id:
            return None
        session_doc = await self.sessions.find_one({"user_id": user_id}, {"_id": 0})
        if not session_doc:
            return None
        session = Session(**session_doc)
        return session.peer_id

    async def get_session(self, peer_id: str | None) -> Session | None:
        if not peer_id:
            return None
        session_doc = await self.sessions.find_one({"peer_id": peer_id}, {"_id": 0})
        if not session_doc:
            return None
        return Session(**session_doc)

    async def delete(self, peer_id: str | None) -> None:
        if peer_id:
            await self.sessions.delete_one({"peer_id": peer_id})
