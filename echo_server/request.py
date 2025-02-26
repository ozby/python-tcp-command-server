from dataclasses import dataclass

from echo_server.validation import Validator


@dataclass
class Command:
    request_id: str
    action: str
    client_id: str | None = None


class RequestParser:
    COMMANDS_WITH_CLIENT_ID = ["SIGN_IN"]
    VALID_COMMANDS = ["SIGN_IN", "SIGN_OUT", "WHOAMI"]

    @classmethod
    def parse(cls, line: str) -> Command:
        parts = line.strip().split("|", 2)

        if len(parts) < 2:
            raise ValueError("Invalid format. Expected: request_id|action[|clientId]")

        request_id = parts[0]
        if not Validator.validate_request_id(request_id):
            raise ValueError("Invalid request_id. Must be 7 lowercase letters (a-z)")

        action = parts[1]
        if action not in cls.VALID_COMMANDS:
            raise ValueError("Unknown command")

        client_id = parts[2] if len(parts) > 2 else None

        if action not in cls.COMMANDS_WITH_CLIENT_ID and client_id is not None:
            raise ValueError("client_id only allowed with SIGN_IN command")
        if action in cls.COMMANDS_WITH_CLIENT_ID and client_id is None:
            raise ValueError(f"{action} command requires client_id")
        if client_id is not None and not Validator.validate_client_id(client_id):
            raise ValueError("client_id must be alphanumeric")

        return Command(
            request_id=request_id,
            action=action,
            client_id=client_id,
        )
