# action.py
from abc import ABC, abstractmethod

from server.services.session_service import SessionService


class Action(ABC):
    def __init__(self, request_id: str, params: list[str], session_service: SessionService):
        self.request_id = request_id
        self.params = params
        self.session_service = session_service

    @abstractmethod
    def validate(self) -> None:
        pass

    @abstractmethod
    def execute(self) -> str:
        pass
