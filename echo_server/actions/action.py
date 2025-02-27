# action.py
from abc import ABC, abstractmethod

from echo_server.session import SessionAuth

class Action(ABC):
    def __init__(self, request_id: str, params: list[str], session_auth: SessionAuth):
        self.request_id = request_id
        self.params = params
        self.session_auth = session_auth

    @abstractmethod
    def validate(self):
        pass

    @abstractmethod
    def execute(self):
        pass