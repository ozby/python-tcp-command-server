# actions.py

from echo_server.actions.action import Action


class SignInAction(Action):
    def validate(self):
        if len(self.params) != 1:
            raise ValueError("SIGN_IN action requires exactly one parameter")
        # Add more validation logic if needed

    def execute(self):
        # Implement the execution logic for SIGN_IN
        pass

class SignOutAction(Action):
    def validate(self):
        if len(self.params) != 0:
            raise ValueError("SIGN_OUT action does not require parameters")

    def execute(self):
        # Implement the execution logic for SIGN_OUT
        pass

class WhoAmIAction(Action):
    def validate(self):
        if len(self.params) != 0:
            raise ValueError("WHOAMI action does not require parameters")

    def execute(self):
        # Implement the execution logic for WHOAMI
        pass

# Add more action classes for other actions