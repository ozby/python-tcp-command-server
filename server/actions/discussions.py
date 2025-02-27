import logging

from server.actions.action import Action
from server.response import Response
from server.services.discussion_service import DiscussionService
from server.services.session_service import SessionService
from server.validation import Validator


class CreateDiscussionAction(Action):
    def validate(self) -> None:
        client_id = SessionService().get_client_id(self.peer_id)
        if (client_id is None):
            raise ValueError("authentication is required")
        
        logging.info(f"params: {self.params}")
        if len(self.params) != 2:
            raise ValueError("action requires two parameters")

        reference, comment = self.params[0], self.params[1]
        if not Validator.validate_reference(reference):
            raise ValueError("reference must be period-delimited alphanumeric")
        logging.info(f"reference: {reference}, comment: {comment}")

    def execute(self) -> str:
        discussion_service = DiscussionService()
        discussion_id = discussion_service.create_discussion(self.params[0], self.params[1], SessionService().get_client_id(self.peer_id))
        return Response(request_id=self.request_id, params=[discussion_id]).serialize()


class CreateReplyAction(Action):
    def validate(self) -> None:
        client_id = SessionService().get_client_id(self.peer_id)
        if (client_id is None):
            raise ValueError("authentication is required")
        
        if len(self.params) != 2:
            raise ValueError("action requires two parameters")

        discussion_id, comment = self.params[0], self.params[1]
        logging.info(f"discussion_id: {discussion_id}, comment: {comment}")

        # if len(self.params) > 0 and not Validator.validate_client_id(self.params[0]):
        #     raise ValueError("client_id must be alphanumeric")

    def execute(self) -> str:
        discussion_id, comment = self.params[0], self.params[1]
        discussion_service = DiscussionService()
        discussion_service.create_reply(discussion_id, comment, SessionService().get_client_id(self.peer_id))
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
        discussion_service = DiscussionService()
        discussion = discussion_service.get_discussion(self.params[0])

        replies = []
        for reply in discussion.replies:
            replies.append(f"{reply.author}|{reply.comment}")
        params = [
            discussion.discussion_id, discussion.reference,
            "(" + ",".join(replies) + ")"]
        return Response(request_id=self.request_id, params=params).serialize()


class ListDiscussionAction(Action):
    def validate(self) -> None:
        if len(self.params) > 1:
            raise ValueError("action can't have more than one parameter")

        # if len(self.params) > 0 and not Validator.validate_client_id(self.params[0]):
        #     raise ValueError("client_id must be alphanumeric")

    def execute(self) -> str:
        discussion_service = DiscussionService()
        discussions = discussion_service.list_discussions()

        # Format discussions into readable output
        discussion_list = []
        for discussion in discussions:
            replies = []
            for reply in discussion.replies:
                replies.append(f"{reply.author}|{reply.comment}")

            discussion_list.append(f"{discussion.discussion_id}|{discussion.reference}|({','.join(replies)})")
        # print(f"discussion_list: {",".join(discussion_list)}")
        return Response(request_id=self.request_id, params=discussion_list).serialize_list()
