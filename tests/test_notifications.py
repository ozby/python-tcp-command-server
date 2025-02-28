import time
from collections.abc import Generator

import pytest

from server.db.entities.notification import NotificationType
from server.services.discussion_service import DiscussionService
from server.services.notification_service import NotificationService
from server.services.session_service import SessionService

# Test data
TEST_PEER_1 = "127.0.0.1:8001"
TEST_PEER_2 = "127.0.0.1:8002"
TEST_PEER_3 = "127.0.0.1:8003"
TEST_PEER_4 = "127.0.0.1:8004"


@pytest.fixture(autouse=True)
async def setup() -> Generator[None, None, None]:
    # Setup test users
    await SessionService().set(TEST_PEER_1, "user1")
    await SessionService().set(TEST_PEER_2, "user2")
    await SessionService().set(TEST_PEER_3, "user3")
    await SessionService().set(TEST_PEER_4, "user4")
    yield
    # Cleanup after each test
    mongo_client = NotificationService().db
    mongo_client.notifications.delete_many({})
    mongo_client.discussions.delete_many({})
    mongo_client.sessions.delete_many({})


def test_reply_notifications() -> None:
    discussion_service = DiscussionService()
    notification_service = NotificationService()

    # Create initial discussion by user1
    discussion_id = discussion_service.create_discussion(
        reference="test.123", comment="Initial discussion", client_id="user1"
    )

    # User2 replies
    discussion_service.create_reply(
        discussion_id=discussion_id, comment="First reply", client_id="user2"
    )

    # Check notifications for user1 (should get notification from user2's reply)
    user1_notifications = notification_service.get_notifications("user1")
    assert len(user1_notifications) == 1
    assert user1_notifications[0].notification_type == NotificationType.REPLY
    assert user1_notifications[0].sender_id == "user2"
    assert user1_notifications[0].recipient_id == "user1"

    # User3 replies
    discussion_service.create_reply(
        discussion_id=discussion_id, comment="Second reply", client_id="user3"
    )

    # Check notifications for user1 and user2
    user1_notifications = notification_service.get_notifications("user1")
    user2_notifications = notification_service.get_notifications("user2")

    assert (
        len(user1_notifications) == 2
    )  # Should have notifications from user2 and user3
    assert len(user2_notifications) == 1  # Should have notification from user3


def test_mention_notifications() -> None:
    discussion_service = DiscussionService()
    notification_service = NotificationService()

    # Create discussion with mentions
    discussion_service.create_discussion(
        reference="test.123",
        comment="Hey @user2 and @user3, check this out!",
        client_id="user1",
    )

    # Check mention notifications
    user2_notifications = notification_service.get_notifications("user2")
    user3_notifications = notification_service.get_notifications("user3")
    user4_notifications = notification_service.get_notifications("user4")

    assert len(user2_notifications) == 1
    assert len(user3_notifications) == 1
    assert len(user4_notifications) == 0  # user4 wasn't mentioned

    assert user2_notifications[0].notification_type == NotificationType.MENTION
    assert user3_notifications[0].notification_type == NotificationType.MENTION


def test_combined_reply_and_mention_notifications() -> None:
    discussion_service = DiscussionService()
    notification_service = NotificationService()

    # User1 creates discussion mentioning user4
    discussion_id = discussion_service.create_discussion(
        reference="test.123",
        comment="Initial discussion mentioning @user4",
        client_id="user1",
    )

    # User2 replies mentioning user3 and user4
    discussion_service.create_reply(
        discussion_id=discussion_id,
        comment="Hey @user3 and @user4, what do you think?",
        client_id="user2",
    )

    # Check notifications
    user1_notifications = notification_service.get_notifications("user1")
    user3_notifications = notification_service.get_notifications("user3")
    user4_notifications = notification_service.get_notifications("user4")

    # User1 should have 1 reply notification from user2
    assert len(user1_notifications) == 1
    assert user1_notifications[0].notification_type == NotificationType.REPLY

    # User3 should have 1 mention notification from user2
    assert len(user3_notifications) == 1
    assert user3_notifications[0].notification_type == NotificationType.MENTION

    # User4 should have 2 mention notifications (from user1 and user2)
    assert len(user4_notifications) == 2
    assert all(
        n.notification_type == NotificationType.MENTION for n in user4_notifications
    )


def test_self_mention_and_reply() -> None:
    discussion_service = DiscussionService()
    notification_service = NotificationService()

    # User1 creates discussion mentioning themselves
    discussion_id = discussion_service.create_discussion(
        reference="test.123",
        comment="Note to @user1: don't forget this!",
        client_id="user1",
    )

    # User1 replies to their own discussion
    discussion_service.create_reply(
        discussion_id=discussion_id,
        comment="Replying to myself and @user1 again",
        client_id="user1",
    )

    # Check notifications - user1 should have no notifications
    user1_notifications = notification_service.get_notifications("user1")
    assert len(user1_notifications) == 0  # No self-notifications


def test_mark_notifications_as_read() -> None:
    discussion_service = DiscussionService()
    notification_service = NotificationService()

    # Create discussion with mentions and replies
    discussion_id = discussion_service.create_discussion(
        reference="test.123", comment="Hey @user2, check this out!", client_id="user1"
    )

    discussion_service.create_reply(
        discussion_id=discussion_id,
        comment="Replying and mentioning @user3",
        client_id="user2",
    )

    # Verify initial notifications
    user1_notifications = notification_service.get_notifications("user1")
    user2_notifications = notification_service.get_notifications("user2")
    user3_notifications = notification_service.get_notifications("user3")

    assert len(user1_notifications) == 1  # Reply notification
    assert len(user2_notifications) == 1  # Mention notification
    assert len(user3_notifications) == 1  # Mention notification

    # Mark notifications as read for user1
    notification_service.mark_as_read("user1", discussion_id)

    # Verify notifications after marking as read
    user1_notifications = notification_service.get_notifications("user1")
    user2_notifications = notification_service.get_notifications("user2")
    assert len(user1_notifications) == 0  # Should be cleared
    assert len(user2_notifications) == 1  # Should remain unchanged


def test_notification_ordering() -> None:
    discussion_service = DiscussionService()
    notification_service = NotificationService()

    # Create discussion
    discussion_id = discussion_service.create_discussion(
        reference="test.123",
        comment="Initial discussion mentioning @user2",
        client_id="user1",
    )

    # Add replies with small time gaps
    time.sleep(0.1)
    discussion_service.create_reply(
        discussion_id=discussion_id,
        comment="First reply mentioning @user2",
        client_id="user3",
    )

    time.sleep(0.1)
    discussion_service.create_reply(
        discussion_id=discussion_id,
        comment="Second reply mentioning @user2",
        client_id="user4",
    )

    # Get notifications for user2
    notifications = notification_service.get_notifications("user2")

    # Verify notifications are ordered by created_at descending
    assert len(notifications) == 3
    for i in range(len(notifications) - 1):
        assert notifications[i].created_at > notifications[i + 1].created_at


def test_invalid_mentions() -> None:
    discussion_service = DiscussionService()
    notification_service = NotificationService()

    # Test mentions with various edge cases
    discussion_service.create_discussion(
        reference="test.123",
        comment="""
        @user2, @user3@invalid @not_a_user
        @@user4 @@ @
        """,
        client_id="user1",
    )

    # Only valid mentions should create notifications
    user2_notifications = notification_service.get_notifications("user2")
    user3_notifications = notification_service.get_notifications("user3")
    user4_notifications = notification_service.get_notifications("user4")

    assert len(user2_notifications) == 1  # Valid mention: @user2,
    assert len(user3_notifications) == 0  # Invalid: @user3@invalid
    assert len(user4_notifications) == 0  # Invalid: @@user4


def test_duplicate_mentions() -> None:
    discussion_service = DiscussionService()
    notification_service = NotificationService()

    # Create discussion with duplicate mentions
    discussion_service.create_discussion(
        reference="test.123",
        comment="Hey @user2 @user2 @user2, multiple mentions!",
        client_id="user1",
    )

    # Should only create one notification despite multiple mentions
    user2_notifications = notification_service.get_notifications("user2")
    assert len(user2_notifications) == 1


def test_mention_in_reply_to_own_discussion() -> None:
    discussion_service = DiscussionService()
    notification_service = NotificationService()

    # User1 creates discussion
    discussion_id = discussion_service.create_discussion(
        reference="test.123", comment="Initial discussion", client_id="user1"
    )

    # User1 replies to their own discussion mentioning others
    discussion_service.create_reply(
        discussion_id=discussion_id,
        comment="Mentioning @user2 and @user3 in my own discussion",
        client_id="user1",
    )

    # Check notifications
    user1_notifications = notification_service.get_notifications("user1")
    user2_notifications = notification_service.get_notifications("user2")
    user3_notifications = notification_service.get_notifications("user3")

    assert len(user1_notifications) == 0  # No self notifications
    assert len(user2_notifications) == 1  # Mention notification
    assert len(user3_notifications) == 1  # Mention notification


def test_performance_many_notifications() -> None:
    discussion_service = DiscussionService()
    notification_service = NotificationService()

    # Create discussion
    discussion_id = discussion_service.create_discussion(
        reference="test.123", comment="Initial discussion", client_id="user1"
    )

    # Add many replies (testing bulk notification creation)
    for i in range(50):
        discussion_service.create_reply(
            discussion_id=discussion_id,
            comment=f"Reply {i} mentioning @user2",
            client_id="user3",
        )

    # Verify notifications were created correctly
    user1_notifications = notification_service.get_notifications("user1")
    user2_notifications = notification_service.get_notifications("user2")

    assert len(user1_notifications) == 50  # Reply notifications
    assert len(user2_notifications) == 50  # Mention notifications


def test_mark_all_as_read() -> None:
    discussion_service = DiscussionService()
    notification_service = NotificationService()

    # Create multiple discussions with notifications
    discussion_id1 = discussion_service.create_discussion(
        reference="test.123",
        comment="First discussion mentioning @user2",
        client_id="user1",
    )

    discussion_id2 = discussion_service.create_discussion(
        reference="test.456",
        comment="Second discussion mentioning @user2",
        client_id="user1",
    )

    # Mark all notifications as read for user2
    notification_service.mark_as_read("user2", discussion_id1)
    notification_service.mark_as_read("user2", discussion_id2)

    # Verify all notifications are cleared
    user2_notifications = notification_service.get_notifications("user2")
    assert len(user2_notifications) == 0


def test_notification_after_mark_as_read() -> None:
    discussion_service = DiscussionService()
    notification_service = NotificationService()

    # Create discussion
    discussion_id = discussion_service.create_discussion(
        reference="test.123",
        comment="Initial discussion mentioning @user2",
        client_id="user1",
    )

    # Mark as read
    notification_service.mark_as_read("user2", discussion_id)

    # Add new reply with mention
    discussion_service.create_reply(
        discussion_id=discussion_id,
        comment="New reply mentioning @user2",
        client_id="user3",
    )

    # Verify new notifications are created after mark as read
    user2_notifications = notification_service.get_notifications("user2")
    assert len(user2_notifications) == 1
    assert user2_notifications[0].sender_id == "user3"
