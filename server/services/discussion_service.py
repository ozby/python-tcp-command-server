import asyncio
from asyncio.log import logger
from dataclasses import dataclass
import datetime
import logging
import random
import string
        

from server.services.service import singleton

@dataclass
class Reply:
    author: str
    comment: str
    date: datetime
    
@dataclass 
class Discussion:
    reference: str
    author: str
    replies: list[Reply]
    date: datetime



@singleton
class DiscussionService:
    def __init__(self):
        self.discussions: dict[str, list[Discussion]] = {}


        discussion_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=7))
        self.discussions[discussion_id].insert(Discussion(reference=reference, author=author, replies=[], date=datetime.datetime.now()))
        logging.info(f"Discussion created: {discussion_id}")
        logging.info(f"Discussions: {self.discussions}")

    def get_discussion(self, reference: str) -> list[str]:
        return self.discussions[reference]