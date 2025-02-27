# action_factory.py

from echo_server.actions.action import Action
from echo_server.actions.actions import SignInAction, SignOutAction, WhoAmIAction


class ActionFactory:
    @staticmethod
    def create_action(action: str, request_id: str, params: list[str]) -> Action:
        if action == "SIGN_IN":
            return SignInAction(request_id, params)
        elif action == "SIGN_OUT":
            return SignOutAction(request_id, params)
        elif action == "WHOAMI":
            return WhoAmIAction(request_id, params)
        # elif action == "CREATE_DISCUSSION":
        #     return CreateDiscussionAction(request_id, params)
        # elif action == "CREATE_REPLY":
        #     return CreateReplyAction(request_id, params)
        # elif action == "GET_DISCUSSION":
        #     return GetDiscussionAction(request_id, params)
        # Add more conditions for other actions
        else:
            raise ValueError("Unknown action")