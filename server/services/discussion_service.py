import logging
import random
import string
from typing import Optional, List

from server.services.service import singleton
from server.db.mongo_client import mongo_client
from server.db.entities.discussion import Discussion
from server.db.entities.reply import Reply


@singleton
class DiscussionService:
    def __init__(self):
        self.db = mongo_client.db
        self.discussions = self.db.discussions
        self.discussions.create_index("discussion_id", unique=True)
        self.discussions.create_index("reference_prefix")

    def _sanitize_comment(self, comment: str) -> str:
        if "," in comment:
            escaped_comment = comment.replace('"', '""')
            return f'"{escaped_comment}"'
        return comment

    def create_discussion(self, reference: str, comment: str, client_id: str) -> str:
        reference_prefix = reference.split(".")[0]
        discussion_id = "".join(
            random.choices(string.ascii_lowercase + string.digits, k=7)
        )

        discussion_doc = {
            "discussion_id": discussion_id,
            "reference_prefix": reference_prefix,
            "reference": reference,
            "client_id": client_id,
            "replies": [
                {"client_id": client_id, "comment": self._sanitize_comment(comment)}
            ]
        }

        self.discussions.insert_one(discussion_doc)
        return discussion_id

    def create_reply(self, discussion_id: str, comment: str, client_id: str) -> str:
        new_reply = {"client_id": client_id, "comment": self._sanitize_comment(comment)}
        self.discussions.update_one(
            {"discussion_id": discussion_id}, 
            {"$push": {"replies": new_reply}}
        )
        return discussion_id

    def get_discussion(self, discussion_id: str) -> Optional[Discussion]:
        discussion_doc = self.discussions.find_one({"discussion_id": discussion_id})
        if not discussion_doc:
            return None

        return Discussion(
            discussion_id=discussion_doc["discussion_id"],
            reference_prefix=discussion_doc["reference_prefix"],
            reference=discussion_doc["reference"],
            client_id=discussion_doc["client_id"],
            replies=[Reply(**reply) for reply in discussion_doc["replies"]]
        )

    def list_discussions(self, reference_prefix: str | None = None) -> List[Discussion]:
        query = {"reference_prefix": reference_prefix} if reference_prefix else {}
        discussion_docs = self.discussions.find(query)

        return [
            Discussion(
                discussion_id=doc["discussion_id"],
                reference_prefix=doc["reference_prefix"],
                reference=doc["reference"],
                client_id=doc["client_id"],
                replies=[Reply(**reply) for reply in doc["replies"]]
            )
            for doc in discussion_docs
        ]
