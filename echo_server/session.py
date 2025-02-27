import asyncio
from asyncio.log import logger


class SessionAuth:
    def __init__(self, writer: asyncio.StreamWriter):
        self.sessions = {}
        self.writer = writer
        self.peer = writer.get_extra_info("peername")
        self.peer_str = f"{self.peer[0]}:{self.peer[1]}"
        logger.info("Sessions: %s", self.sessions)


    def set(self, user_id: str):
        self.sessions[self.peer_str] = user_id

    def get(self):
        return self.sessions[self.peer_str] if self.peer_str in self.sessions else None
        
    def delete(self):
        if self.peer_str in self.sessions:
            del self.sessions[self.peer_str]