from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import final


@dataclass
class CommandContext:
    request_id: str
    params: list[str]
    peer_id: str | None = None


class Command(ABC):
    def __init__(self, context: CommandContext):
        self.context = context

    @abstractmethod
    async def _validate(self) -> None:
        """Validate the command parameters before execution"""
        pass
    @final
    async def execute(self) -> str:
        """Execute the command and return the result
        
        This is a template method that ensures validation is performed before
        actual execution logic.
        """
        await self._validate()
        return await self._execute_impl()

    @abstractmethod
    async def _execute_impl(self) -> str:
        """Implementation of command execution logic
        
        This method should be implemented by subclasses to provide the actual
        execution logic after validation has been performed.
        """
        pass
