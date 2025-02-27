# actions.py

import logging

from server.actions.action import Action
from server.response import Response
from server.services.discussion_service import DiscussionService
from server.validation import Validator


class CreateDiscussionAction(Action):
    def validate(self) -> None:
        logging.info(f"params: {self.params}")
        if len(self.params) != 2:
            raise ValueError("action requires two parameters")

        reference, comment = self.params[0], self.params[1]
        if not Validator.validate_reference(reference):
            raise ValueError("reference must be period-delimited alphanumeric")
        logging.info(f"reference: {reference}, comment: {comment}")

    def execute(self) -> str:
        discussion_service = DiscussionService()
        discussion_service.create_discussion(self.params[0], self.params[1])
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
