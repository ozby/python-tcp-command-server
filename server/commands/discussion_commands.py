import logging
from server.commands.command import Command
from server.response import Response
from server.services.discussion_service import DiscussionService
from server.services.session_service import SessionService
from server.validation import Validator

class CreateDiscussionCommand(Command):
    def _validate(self) -> None:
        client_id = SessionService().get_client_id(self.context.peer_id)
        if client_id is None:
            raise ValueError("authentication is required")

        if len(self.context.params) != 2:
            raise ValueError("action requires two parameters")

        reference, comment = self.context.params[0], self.context.params[1]
        if not Validator.validate_reference(reference):
            raise ValueError("reference must be period-delimited alphanumeric")

    def execute(self) -> str:
        client_id = SessionService().get_client_id(self.context.peer_id)
        if client_id is None:
            raise ValueError("authentication is required")
            
        discussion_service = DiscussionService()
        self._created_discussion_id = discussion_service.create_discussion(
            self.context.params[0],
            self.context.params[1],
            client_id
        )
        return Response(
            request_id=self.context.request_id,
            params=[self._created_discussion_id]
        ).serialize()
    
    def undo(self) -> None:
        if hasattr(self, '_created_discussion_id'):
            discussion_service = DiscussionService()
            discussion_service.delete_discussion(self._created_discussion_id)
    
    def can_undo(self) -> bool:
        return True

class CreateReplyCommand(Command):
    def _validate(self) -> None:
        client_id = SessionService().get_client_id(self.context.peer_id)
        if client_id is None:
            raise ValueError("authentication is required")

        if len(self.context.params) != 2:
            raise ValueError("action requires two parameters")

    def execute(self) -> str:
        client_id = SessionService().get_client_id(self.context.peer_id)
        if client_id is None:
            raise ValueError("authentication is required")
            
        discussion_id, comment = self.context.params[0], self.context.params[1]
        discussion_service = DiscussionService()
        self._discussion_id = discussion_id
        self._reply_id = discussion_service.create_reply(discussion_id, comment, client_id)
        return Response(request_id=self.context.request_id).serialize()
    
    def undo(self) -> None:
        if hasattr(self, '_discussion_id') and hasattr(self, '_reply_id'):
            discussion_service = DiscussionService()
            discussion_service.delete_reply(self._discussion_id, self._reply_id)
    
    def can_undo(self) -> bool:
        return True

class GetDiscussionCommand(Command):
    def _validate(self) -> None:
        if len(self.context.params) != 1:
            raise ValueError("action requires one parameter")

    def execute(self) -> str:
        discussion_service = DiscussionService()
        discussion = discussion_service.get_discussion(self.context.params[0])
        if discussion is None:
            raise ValueError("Discussion not found")

        replies = []
        for reply in discussion.replies:
            replies.append(f"{reply.client_id}|{reply.comment}")
        params = [
            discussion.discussion_id,
            discussion.reference,
            "(" + ",".join(replies) + ")",
        ]
        return Response(request_id=self.context.request_id, params=params).serialize()
    
    def undo(self) -> None:
        pass  # Read-only command, no undo needed

class ListDiscussionsCommand(Command):
    def _validate(self) -> None:
        if len(self.context.params) > 1:
            raise ValueError("action can't have more than one parameter")

    def execute(self) -> str:
        discussion_service = DiscussionService()
        discussions = discussion_service.list_discussions()

        discussion_list = []
        for discussion in discussions:
            replies = []
            for reply in discussion.replies:
                replies.append(f"{reply.client_id}|{reply.comment}")

            discussion_list.append(
                f"{discussion.discussion_id}|{discussion.reference}|({','.join(replies)})"
            )
        return Response(
            request_id=self.context.request_id,
            params=discussion_list
        ).serialize_list()
    
    def undo(self) -> None:
        pass  # Read-only command, no undo needed 