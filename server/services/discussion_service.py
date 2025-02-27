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


    def create_discussion(self, reference: str, comment: str, client_id: str) -> str:
        reference_prefix = reference.split('.')[0]
        discussion_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=7))
        discussion = Discussion(discussion_id=discussion_id,reference_prefix=reference_prefix, reference=reference, author=client_id, replies=[
            Reply(author=client_id, comment=comment)
        ], date=datetime.datetime.now())
        self.discussions[discussion_id] = discussion

        return discussion_id
    
    def create_reply(self, discussion_id: str, comment: str, client_id: str) -> str:
        discussion = self.discussions[discussion_id]
        discussion.replies.append(Reply(author=client_id, comment=comment))
        return discussion_id

    def get_discussion(self, discussion_id: str) -> list[str]:
        return self.discussions[discussion_id]
    
    def list_discussions(self, reference_prefix: str = None) -> list[str]:
        if reference_prefix:
            return [discussion for discussion in self.discussions.values() if discussion.reference_prefix == reference_prefix]
        else:
            return list(self.discussions.values())

        return list(self.discussions.values())