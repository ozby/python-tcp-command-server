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
    ListDiscussionsAction,
)


class ActionFactory:
    @staticmethod
    def execute_action(
        action: str, request_id: str, params: list[str], peer_id: str | None = None
    ) -> Action:
        actions: dict[str, type[Action]] = {
            "SIGN_IN": SignInAction,
            "SIGN_OUT": SignOutAction,
            "WHOAMI": WhoAmIAction,
            "CREATE_DISCUSSION": CreateDiscussionAction,
            "CREATE_REPLY": CreateReplyAction,
            "GET_DISCUSSION": GetDiscussionAction,
            "LIST_DISCUSSIONS": ListDiscussionsAction,
        }

        if action in actions:
            action_class = actions[action]
            return action_class(request_id, params, peer_id)

        raise ValueError("Unknown action")
