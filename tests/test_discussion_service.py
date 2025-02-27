from server.services.discussion_service import DiscussionService

def test_create_discussion():
    discussion_service = DiscussionService()
    discussion_id = discussion_service.create_discussion("xyz.123", "test comment")
    assert discussion_service.discussions[discussion_id].replies[0].comment == "test comment"

def test_create_reply():
    discussion_service = DiscussionService()
    discussion_id = discussion_service.create_discussion("ref.123", "test comment 2")
    discussion_service.create_reply(discussion_id, "test reply")
    assert discussion_service.discussions[discussion_id].replies[1].comment == "test reply"

def test_list_discussions():
    discussion_service = DiscussionService()
    discussions = discussion_service.list_discussions()
    assert len(discussions) == 2
    assert discussions[0].replies[0].comment == "test comment"
    assert discussions[1].replies[0].comment == "test comment 2"
    assert discussions[1].replies[1].comment == "test reply"

    filtered_by_reference_prefix = discussion_service.list_discussions(reference_prefix="xyz")
    assert len(filtered_by_reference_prefix) == 1
    assert filtered_by_reference_prefix[0].replies[0].comment == "test comment"
    
    
def test_get_discussion():
    discussion_service = DiscussionService()
    discussion_id = discussion_service.create_discussion("ref.123", "test comment 3")
    discussion = discussion_service.get_discussion(discussion_id)
    
    assert discussion is not None
    assert discussion.discussion_id == discussion_id
    assert discussion.reference == "ref.123"
    assert discussion.author == "author"
    assert discussion.replies[0].comment == "test comment 3"
