from server.actions.action import Action
from server.actions.auth import (
    SignInAction,
    SignOutAction,
    WhoAmIAction,
)
from server.actions.discussions import (
    CreateDiscussionAction,
    CreateReplyAction,
    GetDiscussionAction,
    ListDiscussionAction,
)


class ActionFactory:
    @staticmethod
    def execute_action(
        action: str,
        request_id: str,
        params: list[str],
    ) -> Action:
        auth_actions = {
            "SIGN_IN": SignInAction,
            "SIGN_OUT": SignOutAction,
            "WHOAMI": WhoAmIAction,
        }

        discussion_actions = {
            "CREATE_DISCUSSION": CreateDiscussionAction,
            "CREATE_REPLY": CreateReplyAction,
            "GET_DISCUSSION": GetDiscussionAction,
            "LIST_DISCUSSIONS": ListDiscussionAction,
        }

        if action in auth_actions:
            action_class = auth_actions[action]
            return action_class(request_id, params)

        if action in discussion_actions:
            action_class = discussion_actions[action]
            return action_class(request_id, params)

        raise ValueError("Unknown action")
