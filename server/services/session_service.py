import asyncio
from asyncio.log import logger

from server.services.service import singleton



@singleton
class SessionService:
    def __init__(self, writer: asyncio.StreamWriter | None = None):
        self.sessions: dict[str, str] = {}
        self.writer = writer
        self.peer = writer.get_extra_info("peername") if writer else None
        self.peer_str = f"{self.peer[0]}:{self.peer[1]}" if self.peer else None
        logger.info("Sessions: %s", self.sessions)

    def set(self, user_id: str) -> None:
        self.sessions[self.peer_str] = user_id

    def get(self) -> str | None:
        return self.sessions[self.peer_str] if self.peer_str in self.sessions else None

    def delete(self) -> None:
        if self.peer_str in self.sessions:
            del self.sessions[self.peer_str]
