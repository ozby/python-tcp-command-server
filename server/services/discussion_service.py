from dataclasses import dataclass
import random
import string
from typing import Optional

from server.services.service import singleton
from server.db.mongo_client import mongo_client


@dataclass
class Reply:
    client_id: str
    comment: str


@dataclass
class Discussion:
    discussion_id: str
    reference_prefix: str
    reference: str
    client_id: str
    replies: list[Reply]


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
            ],
            "date": datetime.datetime.now(),
        }

        self.discussions.insert_one(discussion_doc)
        return discussion_id

    def create_reply(self, discussion_id: str, comment: str, client_id: str) -> str:
        new_reply = {"client_id": client_id, "comment": self._sanitize_comment(comment)}

        self.discussions.update_one(
            {"discussion_id": discussion_id}, {"$push": {"replies": new_reply}}
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
            replies=[Reply(**reply) for reply in discussion_doc["replies"]],
            date=discussion_doc["date"],
        )

    def list_discussions(self, reference_prefix: str = None) -> list[Discussion]:
        query = {"reference_prefix": reference_prefix} if reference_prefix else {}
        discussions = self.discussions.find(query)

        return [
            Discussion(
                discussion_id=doc["discussion_id"],
                reference_prefix=doc["reference_prefix"],
                reference=doc["reference"],
                client_id=doc["client_id"],
                replies=[Reply(**reply) for reply in doc["replies"]],
                date=doc["date"],
            )
            for doc in discussions
        ]
