import logging

from server.commands.command_factory import CommandFactory
from server.validation import Validator

MIN_PART = 2


class Request:

    def __init__(
        self,
        request_id: str,
        action: str,
        params: list[str] | None = None,
        peer_id: str | None = None,
    ):
        if params is None:
            params = []
        self.request_id = request_id
        self.action = action
        self.params = params
        self.peer_id = peer_id

    @staticmethod
    def from_line(line: str, peer_id: str | None = None) -> "Request":
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
        
        # Create and validate the command
        command = CommandFactory.create_command(action, request_id, params, peer_id)
        # Validation is done in Command.__init__

        return Request(request_id, action, params, peer_id)
