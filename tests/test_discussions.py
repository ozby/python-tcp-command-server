import pytest
from unittest.mock import MagicMock

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
    mock_service = DiscussionService()
    mock_service.create_discussion = MagicMock(return_value=discussion_id)
    
    action = CreateDiscussionAction("abcdefg", ["ref.123", "test comment"]) 
    action.discussion_service = mock_service
    
    result = action.execute().rstrip("\n")
    parts = result.split("|")
    assert len(parts) == 2
    assert parts[0] == "abcdefg"
    assert parts[1] == discussion_id
    assert Validator.validate_request_id(parts[1])
    
    mock_service.create_discussion.assert_called_once_with("ref.123", "test comment")

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

def test_list_discussion_validates_params():
    action = ListDiscussionAction("abcdefg", ["disc123"])
    action.validate() # Should not raise
    
    with pytest.raises(ValueError, match="action requires one parameters"):
        ListDiscussionAction("abcdefg", []).validate()
        
    with pytest.raises(ValueError, match="action requires one parameters"):
        ListDiscussionAction("abcdefg", ["disc123", "extra"]).validate()
