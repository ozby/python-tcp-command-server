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
    discussion_id: str
    reference: str
    author: str
    replies: list[Reply]
    date: datetime



@singleton
class DiscussionService:
    def __init__(self):
        self.discussions: dict[str, list[Discussion]] = {}


    def create_discussion(self, reference: str, comment: str) -> str:
        discussion_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=7))
        discussion = Discussion(discussion_id=discussion_id,reference=reference, author="author", replies=[], date=datetime.datetime.now())
        self.discussions[discussion_id] = discussion
        logging.info(f"Discussion created: {discussion_id}")
        logging.info(f"Discussions: {self.discussions}")
        return discussion_id

    def get_discussion(self, reference: str) -> list[str]:
        return self.discussions[reference]