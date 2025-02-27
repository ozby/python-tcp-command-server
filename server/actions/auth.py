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
        SessionService().set(self.params[0])
        return Response(request_id=self.request_id).serialize()


class SignOutAction(Action):
    def validate(self) -> None:
        # if len(self.params) != 0:
        #     raise ValueError("SIGN_OUT action does not require parameters")
        pass

    def execute(self) -> str:
        SessionService().delete()
        return Response(request_id=self.request_id).serialize()


class WhoAmIAction(Action):
    def validate(self) -> None:
        # if len(self.params) != 0:
        #     raise ValueError("WHOAMI action does not require parameters")
        pass

    def execute(self) -> str:
        params = (
            [str(SessionService().get())]
            if SessionService().get() is not None
            else []
        )

        response_data = Response(request_id=self.request_id, params=params)
        return response_data.serialize()
