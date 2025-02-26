from dataclasses import dataclass
from re import compile

@dataclass
class Command:
    request_id: str
    action: str
    client_id: str | None = None


class RequestParser:
    REQUEST_ID_PATTERN = compile(r"^[a-z]{7}$")
    CLIENT_ID_PATTERN = compile(r"^[a-zA-Z0-9]+$")
    COMMANDS_WITH_CLIENT_ID = ["SIGN_IN"]
    VALID_COMMANDS = ["SIGN_IN", "SIGN_OUT", "WHOAMI"]

    @classmethod
    def validate_request_id(cls, request_id: str) -> bool:
        return bool(cls.REQUEST_ID_PATTERN.match(request_id))

    @classmethod
    def validate_client_id(cls, client_id: str) -> bool:
        return bool(cls.CLIENT_ID_PATTERN.match(client_id))

    @classmethod
    def parse(cls, line: str) -> Command:
        parts = line.strip().split("|", 2)

        if len(parts) < 2:
            raise ValueError("Invalid format. Expected: request_id|action[|clientId]")

        request_id = parts[0]
        if not cls.validate_request_id(request_id):
            raise ValueError("Invalid request_id. Must be 7 lowercase letters (a-z)")

        action = parts[1]
        if action not in cls.VALID_COMMANDS:
            raise ValueError("Unknown command")

        client_id = parts[2] if len(parts) > 2 else None

        if action not in cls.COMMANDS_WITH_CLIENT_ID and client_id is not None:
            raise ValueError("client_id only allowed with SIGN_IN command")
        if action in cls.COMMANDS_WITH_CLIENT_ID and client_id is None:
            raise ValueError(f"{action} command requires client_id")
        if client_id is not None and not cls.validate_client_id(client_id):
            raise ValueError("client_id must be alphanumeric")

        return Command(
            request_id=request_id,
            action=action,
            client_id=client_id,
        )
