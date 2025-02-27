import logging
import pytest
from unittest.mock import MagicMock, patch

from server.actions.discussions import CreateDiscussionAction, CreateReplyAction, GetDiscussionAction, ListDiscussionAction
from server.services.discussion_service import DiscussionService
from server.validation import Validator

def test_create_discussion_validates_params():
    action = CreateDiscussionAction("abcdefg", ["ref.123", "test comment"])
    action.validate() # Should not raise

    with pytest.raises(ValueError, match="action requires two parameters"):
        CreateDiscussionAction("abcdefg", []).validate()
        
    with pytest.raises(ValueError, match="action requires two parameters"):
        CreateDiscussionAction("abcdefg", ["ref.123"]).validate()
        
    with pytest.raises(ValueError, match="reference must be period-delimited alphanumeric"):
        CreateDiscussionAction("abcdefg", ["invalid!", "test"]).validate()

def test_create_discussion_executes():
    discussion_id = "abcdzzz"
    with patch('server.actions.discussions.DiscussionService') as mock_service_class:
        mock_service = mock_service_class.return_value
        mock_service.create_discussion.return_value = discussion_id
    
        action = CreateDiscussionAction("abcdefg", ["ref.123", "test comment"]) 
        action.discussion_service = mock_service
        
        result = action.execute().rstrip("\n")
        parts = result.split("|")
        assert len(parts) == 2
        assert parts[0] == "abcdefg"
        assert parts[1] == discussion_id
        assert Validator.validate_request_id(parts[1])
        
        mock_service.create_discussion.assert_called_once_with("ref.123", "test comment")

# def test_create_reply_executes():
    # reply = CreateReplyAction("abcdefg", ["discidi", "test comment"])
    # replied = reply.execute().strip("\n")
    # print(f"replied: {replied}")
    # created_discussion_id = created.execute().strip("\n").split("|")[1]
    # print(f"created_discussion_id: {created_discussion_id}")

    # returned_discussion = GetDiscussionAction("abcdefg", [created_discussion_id])
    # returned = returned_discussion.execute()
    # print(f"returned: {returned}")

def test_get_discussion_executes():
    created = CreateDiscussionAction("abcdefg", ["ref.123", "test comment"])
    created_discussion_id = created.execute().strip("\n").split("|")[1]
    print(f"created_discussion_id: {created_discussion_id}")

    returned_discussion = GetDiscussionAction("abcdefg", [created_discussion_id])
    returned = returned_discussion.execute()
    print(f"returned: {returned}")


def test_create_reply_validates_params():
    action = CreateReplyAction("abcdefg", ["disc123", "test reply"])
    action.validate() # Should not raise
    
    with pytest.raises(ValueError, match="action requires two parameters"):
        CreateReplyAction("abcdefg", []).validate()
        
    with pytest.raises(ValueError, match="action requires two parameters"):
        CreateReplyAction("abcdefg", ["disc123"]).validate()

def test_get_discussion_validates_params():
    action = GetDiscussionAction("abcdefg", ["disc123"])
    action.validate() # Should not raise
    
    with pytest.raises(ValueError, match="action requires one parameters"):
        GetDiscussionAction("abcdefg", []).validate()
        
    with pytest.raises(ValueError, match="action requires one parameters"):
        GetDiscussionAction("abcdefg", ["disc123", "extra"]).validate()



# def test_list_discussion_validates_params():
#     create = CreateDiscussionAction("abcdefg", ["ref.123", "test comment"]) 
#     createResult = create.execute().split("|")[1]
#     create2 = CreateDiscussionAction("zbcdefg", ["ref.234", "test comment2"]) 
#     createResult2 = create2.execute().split("|")[1]

#     action = ListDiscussionAction("abcdefg", [])
#     action.validate() # Should not raise
#     result = action.execute()
#     print(f"\List Result: {result}")  # Print the result for debugging

#     assert result == f"abcdefg|{createResult},{createResult2}"

# def test_list_discussion_executes():
    # create = CreateDiscussionAction("ozbydee", ["ref.123", "test comment"])
    # assert create.execute() == 'ozbydee|dizcuid\n'


    # # action = GetDiscussionAction("request", ["abcdzzz"])
    # action = ListDiscussionAction("request")
    # result = action.execute()
    # assert result == "request|abcdzzz\n"