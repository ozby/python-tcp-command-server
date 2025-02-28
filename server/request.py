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

        if action not in CommandFactory._commands:
            raise ValueError(f"Unknown action: {action}")
        
        if action == "SIGN_IN":
            if len(params) != 1 or not Validator.validate_client_id(params[0]):
                raise ValueError("SIGN_IN requires exactly one alphanumeric parameter")
        elif action == "CREATE_DISCUSSION":
            if len(params) != 2:
                raise ValueError("CREATE_DISCUSSION requires exactly two parameters")
            if not Validator.validate_reference(params[0]):
                raise ValueError("reference must be period-delimited alphanumeric")
        elif action == "CREATE_REPLY":
            if len(params) != 2:
                raise ValueError("CREATE_REPLY requires exactly two parameters")
        elif action == "GET_DISCUSSION":
            if len(params) != 1:
                raise ValueError("GET_DISCUSSION requires exactly one parameter")
        
        return Request(request_id, action, params, peer_id)
