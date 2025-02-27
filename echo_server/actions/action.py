# action.py
from abc import ABC, abstractmethod

class Action(ABC):
    def __init__(self, request_id: str, params: list[str]):
        self.request_id = request_id
        self.params = params

    @abstractmethod
    def validate(self):
        pass

    @abstractmethod
    def execute(self):
        pass