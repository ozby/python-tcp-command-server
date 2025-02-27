# action_factory.py

from echo_server.actions.action import Action
from echo_server.actions.actions import SignInAction, SignOutAction, WhoAmIAction
from echo_server.session import SessionAuth


class ActionFactory:
    @staticmethod
    def create_action(action: str, request_id: str, params: list[str], session_auth: SessionAuth) -> Action:
        if action == "SIGN_IN":
            return SignInAction(request_id, params, session_auth)
        elif action == "SIGN_OUT":
            return SignOutAction(request_id, params, session_auth)
        elif action == "WHOAMI":
            return WhoAmIAction(request_id, params, session_auth)
        # elif action == "CREATE_DISCUSSION":
        #     return CreateDiscussionAction(request_id, params)
        # elif action == "CREATE_REPLY":
        #     return CreateReplyAction(request_id, params)
        # elif action == "GET_DISCUSSION":
        #     return GetDiscussionAction(request_id, params)
        # Add more conditions for other actions
        else:
            raise ValueError("Unknown action")