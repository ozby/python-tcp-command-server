# actions.py

import logging

from echo_server.actions.action import Action
from echo_server.response import Response
from echo_server.validation import Validator


class SignInAction(Action):
    def validate(self) -> None:
        if len(self.params) != 1:
            raise ValueError("SIGN_IN action requires exactly one parameter")

        if len(self.params) > 0 and not Validator.validate_client_id(self.params[0]):
            raise ValueError("client_id must be alphanumeric")

    def execute(self) -> str:
        self.session_auth.set(self.params[0])
        return Response(request_id=self.request_id).serialize()


class SignOutAction(Action):
    def validate(self) -> None:
        # if len(self.params) != 0:
        #     raise ValueError("SIGN_OUT action does not require parameters")
        pass

    def execute(self) -> str:
        self.session_auth.delete()
        return Response(request_id=self.request_id).serialize()


class WhoAmIAction(Action):
    def validate(self) -> None:
        # if len(self.params) != 0:
        #     raise ValueError("WHOAMI action does not require parameters")
        pass

    def execute(self) -> str:
        params = (
            [str(self.session_auth.get())]
            if self.session_auth.get() is not None
            else []
        )

        response_data = Response(request_id=self.request_id, params=params)
        return response_data.serialize()


class CreateDiscussionAction(Action):
    def validate(self) -> None:
        if len(self.params) != 2:
            raise ValueError("action requires two parameters")

        reference, comment = self.params[0], self.params[1]
        if not Validator.validate_reference(reference):
            raise ValueError("reference must be period-delimited alphanumeric")
        logging.info(f"reference: {reference}, comment: {comment}")

    def execute(self) -> str:
        return Response(request_id=self.request_id).serialize()


class CreateReplyAction(Action):
    def validate(self) -> None:
        if len(self.params) != 2:
            raise ValueError("action requires two parameters")

        discussion_id, comment = self.params[0], self.params[1]
        logging.info(f"discussion_id: {discussion_id}, comment: {comment}")

        # if len(self.params) > 0 and not Validator.validate_client_id(self.params[0]):
        #     raise ValueError("client_id must be alphanumeric")

    def execute(self) -> str:
        return Response(request_id=self.request_id).serialize()


class GetDiscussionAction(Action):
    def validate(self) -> None:
        if len(self.params) != 1:
            raise ValueError("action requires one parameters")

        discussion_id = self.params[0]
        logging.info(f"discussion_id: {discussion_id}")

        # if len(self.params) > 0 and not Validator.validate_client_id(self.params[0]):
        #     raise ValueError("client_id must be alphanumeric")

    def execute(self) -> str:
        return Response(request_id=self.request_id).serialize()


class ListDiscussionAction(Action):
    def validate(self) -> None:
        if len(self.params) != 1:
            raise ValueError("action requires one parameters")

        discussion_id = self.params[0]
        logging.info(f"discussion_id: {discussion_id}")

        # if len(self.params) > 0 and not Validator.validate_client_id(self.params[0]):
        #     raise ValueError("client_id must be alphanumeric")

    def execute(self) -> str:
        return Response(request_id=self.request_id).serialize()
