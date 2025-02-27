# actions.py

from echo_server.actions.action import Action
from echo_server.response import Response


class SignInAction(Action):
    def validate(self):
        if len(self.params) != 1:
            raise ValueError("SIGN_IN action requires exactly one parameter")
        # Add more validation logic if needed

    def execute(self):
        self.session_auth.set(self.params[0])
        return Response(request_id=self.request_id).serialize()

class SignOutAction(Action):
    def validate(self):
        if len(self.params) != 0:
            raise ValueError("SIGN_OUT action does not require parameters")

    def execute(self):
        self.session_auth.delete()
        return Response(request_id=self.request_id).serialize()

class WhoAmIAction(Action):
    def validate(self):
        if len(self.params) != 0:
            raise ValueError("WHOAMI action does not require parameters")

    def execute(self):
        params = ([self.session_auth.get()] if self.session_auth.get() is not None else [])
        response_data = Response(request_id=self.request_id, params=params)
        return response_data.serialize()

# Add more action classes for other actions