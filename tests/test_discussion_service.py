from server.services.discussion_service import DiscussionService
from server.services.session_service import SessionService
from tests.test_discussions import TEST_PEER_ID


def test_create_discussion():
    service = DiscussionService()
    discussion_id = service.create_discussion(
        reference="test.123", comment="Test comment", client_id="user1"
    )

    # Verify discussion was created
    discussion = service.get_discussion(discussion_id)
    assert discussion is not None
    assert discussion.reference == "test.123"
    assert discussion.client_id == "user1"
    assert len(discussion.replies) == 1
    assert discussion.replies[0].comment == "Test comment"


def test_create_reply():
    service = DiscussionService()
    discussion_id = service.create_discussion(
        reference="test.123", comment="Initial comment", client_id="user1"
    )

    # Add reply
    service.create_reply(
        discussion_id=discussion_id, comment="Reply comment", client_id="user2"
    )

    # Verify reply was added
    discussion = service.get_discussion(discussion_id)
    assert len(discussion.replies) == 2
    assert discussion.replies[1].client_id == "user2"
    assert discussion.replies[1].comment == "Reply comment"


def test_list_discussions():
    service = DiscussionService()

    # Create discussions with different prefixes
    service.create_discussion("test1.123", "Comment 1", "user1")
    service.create_discussion("test1.456", "Comment 2", "user1")
    service.create_discussion("test2.789", "Comment 3", "user2")

    # List discussions with prefix filter
    test1_discussions = service.list_discussions(reference_prefix="test1")
    assert len(test1_discussions) == 2

    # List all discussions
    all_discussions = service.list_discussions()
    assert len(all_discussions) == 3


def test_get_discussion():
    discussion_service = DiscussionService()
    discussion_id = discussion_service.create_discussion(
        "ref.123", "test comment 3", SessionService().get_client_id(TEST_PEER_ID)
    )
    discussion = discussion_service.get_discussion(discussion_id)

    assert discussion is not None
    assert discussion.discussion_id == discussion_id
    assert discussion.reference == "ref.123"
    assert discussion.client_id == SessionService().get_client_id(TEST_PEER_ID)
    assert discussion.replies[0].comment == "test comment 3"
