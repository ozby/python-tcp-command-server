from server.actions.action import Action
from server.response import Response
from server.services.session_service import SessionService
from server.validation import Validator


class SignInAction(Action):
    def validate(self) -> None:
        if len(self.params) != 1:
            raise ValueError("SIGN_IN action requires exactly one parameter")

        if len(self.params) > 0 and not Validator.validate_client_id(self.params[0]):
            raise ValueError("client_id must be alphanumeric")

    def execute(self) -> str:
        if self.peer_id is None:
            raise ValueError("peer_id is required")
        session_service = SessionService()
        session_service.set(peer_id=self.peer_id, user_id=self.params[0])
        return Response(request_id=self.request_id).serialize()


class SignOutAction(Action):
    def validate(self) -> None:
        # if len(self.params) != 0:
        #     raise ValueError("SIGN_OUT action does not require parameters")
        pass

    def execute(self) -> str:
        session_service = SessionService()
        session_service.delete(peer_id=self.peer_id)
        return Response(request_id=self.request_id).serialize()


class WhoAmIAction(Action):
    def validate(self) -> None:
        # if len(self.params) != 0:
        #     raise ValueError("WHOAMI action does not require parameters")
        pass

    def execute(self) -> str:
        session_service = SessionService()
        client_id = session_service.get_client_id(peer_id=self.peer_id)
        params = [client_id] if client_id is not None else None
        return Response(request_id=self.request_id, params=params).serialize()
