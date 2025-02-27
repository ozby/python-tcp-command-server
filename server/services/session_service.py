import asyncio
from asyncio.log import logger
import logging

from server.services.service import singleton



@singleton
class SessionService:
    def __init__(self):
        self.sessions: dict[str, str] = {}

    def set(self, peer_id: str, user_id: str) -> None:
        logging.info(f"Setting session for {peer_id} to {user_id}")
        self.sessions[peer_id] = user_id

    def get_client_id(self, peer_id: str | None) -> str | None:
        return self.sessions[peer_id] if peer_id is not None and peer_id in self.sessions else None
    
    def delete(self, peer_id: str | None) -> None:
        if peer_id is not None and peer_id in self.sessions:
            del self.sessions[peer_id]
