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
        # Call synchronous validation - child classes should override this
        # if they need async validation
        self.validate_sync()
    
    def validate_sync(self) -> None:
        """Synchronous validation that can be called from __init__
        Derived classes with async validation should override this to do basic checks
        and implement full validation in _validate"""
        pass

    @abstractmethod
    async def _validate(self) -> None:
        """Validate the command parameters before execution"""
        pass

    @abstractmethod
    async def execute(self) -> str:
        """Execute the command and return the result"""
        pass

    @abstractmethod
    def undo(self) -> None:
        """Undo the command execution if supported"""
        pass

    def can_undo(self) -> bool:
        """Return whether this command supports undo operation"""
        return False
