from server.commands.command import Command, CommandContext
from server.response import Response
from server.services.session_service import SessionService
from server.validation import Validator


class SignInCommand(Command):
    def __init__(
        self, context: CommandContext, session_service: SessionService
    ) -> None:
        super().__init__(context)
        self.session_service = session_service

    async def _validate(self) -> None:
        if len(self.context.params) != 1:
            raise ValueError("SIGN_IN action requires exactly one parameter")

        if not Validator.validate_client_id(self.context.params[0]):
            raise ValueError("client_id must be alphanumeric")

    async def _execute_impl(self) -> str:
        if self.context.peer_id is None:
            raise ValueError("peer_id is required")

        await self.session_service.set(
            peer_id=self.context.peer_id, user_id=self.context.params[0]
        )
        return Response(request_id=self.context.request_id).serialize()


class SignOutCommand(Command):
    def __init__(
        self, context: CommandContext, session_service: SessionService
    ) -> None:
        super().__init__(context)
        self.session_service = session_service
        self._previous_user_id: str | None = None

    async def _validate(self) -> None:
        pass

    async def _execute_impl(self) -> str:
        self._previous_user_id = await self.session_service.get_client_id(
            self.context.peer_id
        )
        await self.session_service.delete(peer_id=self.context.peer_id)
        return Response(request_id=self.context.request_id).serialize()


class WhoAmICommand(Command):
    def __init__(
        self, context: CommandContext, session_service: SessionService
    ) -> None:
        super().__init__(context)
        self.session_service = session_service

    async def _validate(self) -> None:
        pass

    async def _execute_impl(self) -> str:
        client_id = await self.session_service.get_client_id(self.context.peer_id)
        params = [client_id] if client_id is not None else None
        return Response(request_id=self.context.request_id, params=params).serialize()
