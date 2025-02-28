from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class CommandContext:
    request_id: str
    params: list[str]
    peer_id: str | None = None


class Command(ABC):
    def __init__(self, context: CommandContext):
        self.context = context
        self._validate()

    @abstractmethod
    def _validate(self) -> None:
        """Validate the command parameters before execution"""
        pass

    @abstractmethod
    def execute(self) -> str:
        """Execute the command and return the result"""
        pass

    @abstractmethod
    def undo(self) -> None:
        """Undo the command execution if supported"""
        pass

    def can_undo(self) -> bool:
        """Return whether this command supports undo operation"""
        return False
