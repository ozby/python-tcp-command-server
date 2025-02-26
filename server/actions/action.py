from abc import ABC, abstractmethod


class Action(ABC):
    def __init__(self, request_id: str, params: list[str], peer_id: str | None = None):
        self.request_id = request_id
        self.params = params
        self.peer_id = peer_id

    @abstractmethod
    def validate(self) -> None:
        pass

    @abstractmethod
    def execute(self) -> str:
        pass
