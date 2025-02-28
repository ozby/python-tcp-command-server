from abc import ABC, abstractmethod
from typing import Any


class Action(ABC):
    def __init__(self, request_id: str, params: list[str], peer_id: str) -> None:
        self.request_id = request_id
        self.params = params
        self.peer_id = peer_id

    @abstractmethod
    def execute(self) -> str:
        pass

    @abstractmethod
    def validate(self) -> None:
        pass


# Ensure all classes that inherit from Action implement both methods

# Make sure all subclasses (CreateDiscussionAction, CreateReplyAction, etc.)
# implement both execute() and validate()
