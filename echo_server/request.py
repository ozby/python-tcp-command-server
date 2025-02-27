from echo_server.actions.action_factory import ActionFactory
from echo_server.validation import Validator

MIN_PART = 2
COMMANDS_WITH_CLIENT_ID = ["SIGN_IN"]
VALID_COMMANDS = ["SIGN_IN", "SIGN_OUT", "WHOAMI", "CREATE_DISCUSSION", "CREATE_REPLY", "GET_DISCUSSION",
                  "LIST_DISCUSSIONS"]


class Request:

    def __init__(self, request_id: str, action: str, params: list[str] | None = None):
        if params is None:
            params = []
        self.request_id = request_id
        self.action = action
        self.params = params

    @staticmethod
    def from_line(line: str):
        parts = line.strip().split("|", MIN_PART)

        if len(parts) < MIN_PART:
            raise ValueError("Invalid format. Expected: request_id|action[|params]")

        request_id = parts[0]
        if not Validator.validate_request_id(request_id):
            raise ValueError("Invalid request_id. Must be 7 lowercase letters (a-z)")

        action = parts[1]
        if action not in VALID_COMMANDS:
            raise ValueError("Unknown action")

        params = parts[2:] if len(parts) > MIN_PART else []

        # action = ActionFactory.create_action(action, request_id, params)
        # action.validate()

        if action not in COMMANDS_WITH_CLIENT_ID and len(params) > 0:
            raise ValueError("client_id only allowed with SIGN_IN action")
        if action in COMMANDS_WITH_CLIENT_ID and len(params) == 0:
            raise ValueError(f"{action} action requires third parameter")
        if len(params) > 0 and not Validator.validate_client_id(params[0]):
            raise ValueError("client_id must be alphanumeric")

        return Request(request_id, action, params)
