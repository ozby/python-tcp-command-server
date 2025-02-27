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
    
@dataclass 
class Discussion:
    discussion_id: str
    reference_prefix: str
    reference: str
    author: str
    replies: list[Reply]
    date: datetime



@singleton
class DiscussionService:
    def __init__(self):
        self.discussions: dict[str, Discussion] = {}


    def create_discussion(self, reference: str, comment: str) -> str:
        reference_prefix = reference.split('.')[0]
        discussion_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=7))
        discussion = Discussion(discussion_id=discussion_id,reference_prefix=reference_prefix, reference=reference, author="author", replies=[
            Reply(author="author", comment=comment)
        ], date=datetime.datetime.now())
        self.discussions[discussion_id] = discussion
        logging.info(f"Discussion created: {discussion_id}")
        logging.info(f"{discussion}")
        return discussion_id

    def get_discussion(self, discussion_id: str) -> list[str]:
        return self.discussions[discussion_id]
    
    def list_discussions(self) -> list[str]:
        print(f"keys: {",".join(self.discussions.keys())}")
        print(f"values: {self.discussions.values()}")
        print(f"items: {self.discussions.items()}")

        replies = []
        for discussion in self.discussions.values():
            for reply in discussion.replies:
                replies.append(f"{reply.author}|{reply.comment}")
        return ",".join(replies)