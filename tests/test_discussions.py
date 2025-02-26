import logging
import pytest
from unittest.mock import MagicMock, patch

from server.actions.discussions import CreateDiscussionAction, CreateReplyAction, GetDiscussionAction, ListDiscussionAction
from server.services.discussion_service import DiscussionService
from server.services.session_service import SessionService
from server.validation import Validator

TEST_PEER_ID = "127.0.0.1:89899"

def test_create_discussion_validates_params():
    SessionService().set(TEST_PEER_ID, "tester_client_1")
    action = CreateDiscussionAction("abcdefg", ["ref.123", "test comment"], TEST_PEER_ID)
    action.validate() # Should not raise

    with pytest.raises(ValueError, match="action requires two parameters"):
        CreateDiscussionAction("abcdefg", [], TEST_PEER_ID).validate()
        
    with pytest.raises(ValueError, match="action requires two parameters"):
        CreateDiscussionAction("abcdefg", ["ref.123"], TEST_PEER_ID).validate()
        
    with pytest.raises(ValueError, match="reference must be period-delimited alphanumeric"):
        CreateDiscussionAction("abcdefg", ["invalid!", "test"], TEST_PEER_ID).validate()

def test_create_discussion_executes():
    discussion_id = "abcdzzz"
    with patch('server.actions.discussions.DiscussionService') as mock_service_class:
        mock_service = mock_service_class.return_value
        mock_service.create_discussion.return_value = discussion_id
    
        action = CreateDiscussionAction("abcdefg", ["ref.123", "test comment"], TEST_PEER_ID) 
        action.discussion_service = mock_service
        
        result = action.execute().rstrip("\n")
        parts = result.split("|")
        assert len(parts) == 2
        assert parts[0] == "abcdefg"
        assert parts[1] == discussion_id
        assert Validator.validate_request_id(parts[1])
        
        mock_service.create_discussion.assert_called_once_with("ref.123", "test comment", SessionService().get_client_id(TEST_PEER_ID))

def test_create_reply_executes():
    created = CreateDiscussionAction("abcdefg", ["ref.123", "test comment"], TEST_PEER_ID)
    created_discussion_id = created.execute().strip("\n").split("|")[1]

    reply = CreateReplyAction("abcdefg", [created_discussion_id, "test reply yooo"], TEST_PEER_ID)
    replied = reply.execute()
    print(f"replied: {replied}")

    returned_discussion = GetDiscussionAction("abcdefg", [created_discussion_id], TEST_PEER_ID)
    returned = returned_discussion.execute()
    assert '"' not in returned
    print(f"returned discussion after reply: {returned}")

def test_create_reply_executes_with_comma():
    created = CreateDiscussionAction("abcdefg", ["ref.123", "test comment"], TEST_PEER_ID)
    created_discussion_id = created.execute().strip("\n").split("|")[1]

    reply = CreateReplyAction("abcdefg", [created_discussion_id, "test reply, yooo"], TEST_PEER_ID)
    replied = reply.execute()
    print(f"replied: {replied}")

    returned_discussion = GetDiscussionAction("abcdefg", [created_discussion_id], TEST_PEER_ID)
    returned = returned_discussion.execute()
    assert '"' in returned
    print(f"returned discussion after reply: {returned}")

def test_get_discussion_executes():
    created = CreateDiscussionAction("abcdefg", ["ref.123", "test comment"], TEST_PEER_ID)
    created_discussion_id = created.execute().strip("\n").split("|")[1]
    print(f"created_discussion_id: {created_discussion_id}")

    returned_discussion = GetDiscussionAction("abcdefg", [created_discussion_id], TEST_PEER_ID)
    returned = returned_discussion.execute()
    assert returned == f"abcdefg|{created_discussion_id}|ref.123|({SessionService().get_client_id(TEST_PEER_ID)}|test comment)\n"


def test_create_reply_validates_params():
    action = CreateReplyAction("abcdefg", ["disc123", "test reply"], TEST_PEER_ID)
    action.validate() # Should not raise
    
    with pytest.raises(ValueError, match="action requires two parameters"):
        CreateReplyAction("abcdefg", [], TEST_PEER_ID).validate()
        
    with pytest.raises(ValueError, match="action requires two parameters"):
        CreateReplyAction("abcdefg", ["disc123"], TEST_PEER_ID).validate()

def test_get_discussion_validates_params():
    action = GetDiscussionAction("abcdefg", ["disc123"])
    action.validate() # Should not raise
    
    with pytest.raises(ValueError, match="action requires one parameters"):
        GetDiscussionAction("abcdefg", []).validate()
        
    with pytest.raises(ValueError, match="action requires one parameters"):
        GetDiscussionAction("abcdefg", ["disc123", "extra"]).validate()



def test_list_discussion_validates_params():
    created = CreateDiscussionAction("abcdefg", ["ndgdojs.15s", "test comment"], TEST_PEER_ID)
    created_discussion_id = created.execute().strip("\n").split("|")[1]

    reply = CreateReplyAction("replyaa", [created_discussion_id, "I love this video. What did you use to make it?"], TEST_PEER_ID)
    replied = reply.execute()
    
    reply = CreateReplyAction("replybb", [created_discussion_id, "I used something called \"Synthesia\", it's pretty cool!"], TEST_PEER_ID)
    replied = reply.execute()

    created = CreateDiscussionAction("zzzzccs", ["asdasds.15s", "test comment"], TEST_PEER_ID)
    created_discussion_id = created.execute().strip("\n").split("|")[1]
    
    reply = CreateReplyAction("replyaa", [created_discussion_id, "sadsdsadas"], TEST_PEER_ID)
    replied = reply.execute()
    
    reply = CreateReplyAction("replybb", [created_discussion_id, "pdskfdsjfds"], TEST_PEER_ID)
    replied = reply.execute()


def test_list_discussion_executes():
    action = ListDiscussionAction("abcdefg", [])
    result = action.execute()
    print(f"result: {result}")
    # create = CreateDiscussionAction("ozbydee", ["ref.123", "test comment"])
    # assert create.execute() == 'ozbydee|dizcuid\n'


    # # action = GetDiscussionAction("request", ["abcdzzz"])
    # action = ListDiscussionAction("request")
    # result = action.execute()
    # assert result == "request|abcdzzz\n"