from collections.abc import Coroutine
from typing import Any

from server.commands.command import Command, CommandContext
from server.response import Response
from server.services.discussion_service import DiscussionService
from server.services.session_service import SessionService
from server.validation import Validator


class CreateDiscussionCommand(Command):
    def __init__(
        self,
        context: CommandContext,
        discussion_service: DiscussionService,
        session_service: SessionService,
    ) -> None:
        super().__init__(context)
        self.discussion_service = discussion_service
        self.session_service = session_service
        self._created_discussion_id: str | None = None
        self._delete_coroutine: Coroutine[Any, Any, None] | None = None

    def validate_sync(self) -> None:
        if len(self.context.params) != 2:
            raise ValueError("action requires two parameters")

        reference, _comment = self.context.params[0], self.context.params[1]
        if not Validator.validate_reference(reference):
            raise ValueError("reference must be period-delimited alphanumeric")

    async def _validate(self) -> None:
        client_id = await self.session_service.get_client_id(self.context.peer_id)
        if client_id is None:
            raise ValueError("authentication is required")

    async def execute(self) -> str:
        client_id = await self.session_service.get_client_id(self.context.peer_id)
        if client_id is None:
            raise ValueError("authentication is required")

        created_id = await self.discussion_service.create_discussion(
            self.context.params[0], self.context.params[1], client_id
        )
        self._created_discussion_id = created_id
        return Response(
            request_id=self.context.request_id, params=[created_id]
        ).serialize()


class CreateReplyCommand(Command):
    def __init__(
        self,
        context: CommandContext,
        discussion_service: DiscussionService,
        session_service: SessionService,
    ) -> None:
        super().__init__(context)
        self.discussion_service = discussion_service
        self.session_service = session_service
        self._discussion_id: str | None = None
        self._reply_id: str | None = None

    def validate_sync(self) -> None:
        if len(self.context.params) != 2:
            raise ValueError("action requires two parameters")

    async def _validate(self) -> None:
        client_id = await self.session_service.get_client_id(self.context.peer_id)
        if client_id is None:
            raise ValueError("authentication is required")

    async def execute(self) -> str:
        client_id = await self.session_service.get_client_id(self.context.peer_id)
        if client_id is None:
            raise ValueError("authentication is required")

        discussion_id, comment = self.context.params[0], self.context.params[1]
        self._discussion_id = discussion_id
        reply_id = await self.discussion_service.create_reply(
            discussion_id, comment, client_id
        )
        self._reply_id = reply_id
        return Response(request_id=self.context.request_id).serialize()


class GetDiscussionCommand(Command):
    def __init__(
        self, context: CommandContext, discussion_service: DiscussionService
    ) -> None:
        super().__init__(context)
        self.discussion_service = discussion_service

    def validate_sync(self) -> None:
        if len(self.context.params) != 1:
            raise ValueError("action requires one parameter")

    async def _validate(self) -> None:
        pass

    async def execute(self) -> str:
        discussion = await self.discussion_service.get_discussion(
            self.context.params[0]
        )
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


class ListDiscussionsCommand(Command):
    def __init__(
        self, context: CommandContext, discussion_service: DiscussionService
    ) -> None:
        super().__init__(context)
        self.discussion_service = discussion_service

    def validate_sync(self) -> None:
        if len(self.context.params) > 1:
            raise ValueError("action can't have more than one parameter")

    async def _validate(self) -> None:
        pass

    async def execute(self) -> str:
        discussions = await self.discussion_service.list_discussions()

        discussion_list = []
        for discussion in discussions:
            replies = []
            for reply in discussion.replies:
                replies.append(f"{reply.client_id}|{reply.comment}")

            discussion_list.append(
                f"{discussion.discussion_id}|{discussion.reference}|({','.join(replies)})"
            )
        return Response(
            request_id=self.context.request_id, params=discussion_list
        ).serialize_list()
