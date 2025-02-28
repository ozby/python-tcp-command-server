import random
import re
import string
from typing import Dict, Any

from server.db.entities.discussion import Discussion
from server.db.entities.reply import Reply
from server.db.mongo_client import mongo_client
from server.services.notification_service import NotificationService
from server.services.service import singleton


@singleton
class DiscussionService:
    MENTION_PATTERN = re.compile(r"(?<!@)@(\w+)(?=[\s,.!?]|$)")

    def __init__(self) -> None:
        self.db = mongo_client.db
        self.discussions = self.db.discussions
        self.discussions.create_index("discussion_id", unique=True)
        self.discussions.create_index("reference_prefix")
        self.notification_service = NotificationService()

    def _sanitize_comment(self, comment: str) -> str:
        if "," in comment:
            escaped_comment = comment.replace('"', '""')
            return f'"{escaped_comment}"'
        return comment

    def _get_unique_participants(self, discussion_doc: Dict[str, Any]) -> set[str]:
        """Get unique client_ids from a discussion's replies"""
        participants = {discussion_doc["client_id"]}  # Include discussion creator
        for reply in discussion_doc["replies"]:
            participants.add(reply["client_id"])
        return participants

    def _extract_mentions(self, comment: str) -> set[str]:
        """Extract mentioned client_ids from a comment"""
        return set(self.MENTION_PATTERN.findall(comment))

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
        }

        self.discussions.insert_one(discussion_doc)

        # Handle mentions in the initial comment
        mentioned_users = self._extract_mentions(comment)
        if mentioned_users:
            self.notification_service.create_mention_notifications(
                discussion_id=discussion_id,
                sender_id=client_id,
                mentioned_ids=list(mentioned_users),
            )

        return discussion_id

    def create_reply(self, discussion_id: str, comment: str, client_id: str) -> str:
        # First get the current discussion to find participants
        discussion_doc = self.discussions.find_one(
            {"discussion_id": discussion_id}, {"_id": 0}
        )
        if not discussion_doc:
            raise ValueError(f"Discussion {discussion_id} not found")

        # Get unique participants before adding the new reply, excluding the reply author
        participants = self._get_unique_participants(discussion_doc) - {client_id}

        # Add the new reply
        new_reply = {"client_id": client_id, "comment": self._sanitize_comment(comment)}
        self.discussions.update_one(
            {"discussion_id": discussion_id}, {"$push": {"replies": new_reply}}
        )

        # Create reply notifications for all participants except the reply author
        self.notification_service.create_reply_notifications(
            discussion_id=discussion_id,
            sender_id=client_id,
            recipient_ids=list(participants),
        )

        # Handle mentions in the reply
        mentioned_users = self._extract_mentions(comment)
        if mentioned_users:
            self.notification_service.create_mention_notifications(
                discussion_id=discussion_id,
                sender_id=client_id,
                mentioned_ids=list(mentioned_users),
            )

        return discussion_id

    def get_discussion(self, discussion_id: str) -> Discussion:
        discussion_doc = self.discussions.find_one(
            {"discussion_id": discussion_id}, {"_id": 0}
        )
        if not discussion_doc:
            raise ValueError(f"Discussion {discussion_id} not found")

        return Discussion(
            discussion_id=discussion_doc["discussion_id"],
            reference_prefix=discussion_doc["reference_prefix"],
            reference=discussion_doc["reference"],
            client_id=discussion_doc["client_id"],
            replies=[Reply(**reply) for reply in discussion_doc["replies"]],
        )

    def list_discussions(self, reference_prefix: str | None = None) -> list[Discussion]:
        query = {"reference_prefix": reference_prefix} if reference_prefix else {}
        discussion_docs = self.discussions.find(query, {"_id": 0})

        return [
            Discussion(
                discussion_id=doc["discussion_id"],
                reference_prefix=doc["reference_prefix"],
                reference=doc["reference"],
                client_id=doc["client_id"],
                replies=[Reply(**reply) for reply in doc["replies"]],
            )
            for doc in discussion_docs
        ]
