# action_factory.py

from server.actions.action import Action
from server.actions.actions import (
    CreateDiscussionAction,
    CreateReplyAction,
    GetDiscussionAction,
    ListDiscussionAction,
    SignInAction,
    SignOutAction,
    WhoAmIAction,
)
from server.session import SessionAuth


class ActionFactory:
    @staticmethod
    def create_action(
        action: str,
        request_id: str,
        params: list[str],
        session_auth: SessionAuth,
    ) -> Action:
        action_map = {
            "SIGN_IN": SignInAction,
            "SIGN_OUT": SignOutAction,
            "WHOAMI": WhoAmIAction,
            "CREATE_DISCUSSION": CreateDiscussionAction,
            "CREATE_REPLY": CreateReplyAction,
            "GET_DISCUSSION": GetDiscussionAction,
            "LIST_DISCUSSIONS": ListDiscussionAction,
        }

        action_class = action_map.get(action)
        if action_class is None:
            raise ValueError("Unknown action")

        return action_class(request_id, params, session_auth)
