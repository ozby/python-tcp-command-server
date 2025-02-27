import logging

from server.actions.action_factory import ActionFactory
from server.validation import Validator

MIN_PART = 2


class Request:

    def __init__(self, request_id: str, action: str, params: list[str] | None = None):
        if params is None:
            params = []
        self.request_id = request_id
        self.action = action
        self.params = params

    @staticmethod
    def from_line(line: str) -> "Request":
        parts = [part for part in line.strip().split("|") if part]

        if len(parts) < MIN_PART:
            raise ValueError("Invalid format. Expected: request_id|action[|params]")

        request_id = parts[0]
        if not Validator.validate_request_id(request_id):
            raise ValueError("Invalid request_id. Must be 7 lowercase letters (a-z)")

        logging.info(f"parts: {parts}")
        action = parts[1]
        params = parts[2:] if len(parts) >= MIN_PART else []
        logging.info(f"params: {params}")
        action_man = ActionFactory.execute_action(action, request_id, params)
        action_man.validate()

        return Request(request_id, action, params)
