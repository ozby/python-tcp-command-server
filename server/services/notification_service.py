import logging
from datetime import datetime

from server.db.entities.notification import Notification, NotificationType
from server.db.mongo_client import mongo_client
from server.services.service import singleton


@singleton
class NotificationService:
    def __init__(self) -> None:
        self.db = mongo_client.db
        self.notifications = self.db.notifications
        self.notifications.create_index([("recipient_id", 1), ("discussion_id", 1)])
        self.notifications.create_index("created_at")

    def create_reply_notifications(
        self, discussion_id: str, sender_id: str, recipient_ids: list[str]
    ) -> None:
        """Create reply notifications for all recipients except the sender"""
        if not recipient_ids:
            return

        notifications = [
            {
                "discussion_id": discussion_id,
                "recipient_id": recipient_id,
                "sender_id": sender_id,
                "notification_type": NotificationType.REPLY.value,
                "created_at": datetime.now(),
            }
            for recipient_id in recipient_ids
            if recipient_id != sender_id  # Don't notify the sender
        ]

        if notifications:
            self.notifications.insert_many(notifications)
            logging.info(
                f"Created {len(notifications)} reply notifications for discussion {discussion_id}"
            )

    def create_mention_notifications(
        self, discussion_id: str, sender_id: str, mentioned_ids: list[str]
    ) -> None:
        """Create mention notifications for all mentioned users except the sender"""
        if not mentioned_ids:
            return

        notifications = [
            {
                "discussion_id": discussion_id,
                "recipient_id": recipient_id,
                "sender_id": sender_id,
                "notification_type": NotificationType.MENTION.value,
                "created_at": datetime.now(),
            }
            for recipient_id in mentioned_ids
            if recipient_id != sender_id  # Don't notify if someone mentions themselves
        ]

        if notifications:
            self.notifications.insert_many(notifications)
            logging.info(
                f"Created {len(notifications)} mention notifications for discussion {discussion_id}"
            )

    def get_notifications(self, recipient_id: str) -> list[Notification]:
        """Get all notifications for a recipient"""
        notification_docs = self.notifications.find(
            {"recipient_id": recipient_id}, {"_id": 0}
        ).sort("created_at", -1)

        return [
            Notification(
                **{
                    **doc,
                    "notification_type": NotificationType(doc["notification_type"]),
                }
            )
            for doc in notification_docs
        ]

    def mark_as_read(self, recipient_id: str, discussion_id: str) -> None:
        """Mark notifications as read for a specific discussion"""
        self.notifications.delete_many(
            {"recipient_id": recipient_id, "discussion_id": discussion_id}
        )
