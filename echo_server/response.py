from dataclasses import dataclass

from echo_server.validation import Validator


class Response:
    # request_id: str
    # client_id: str | None = None
    def __init__(self, request_id: str, client_id: str | None = None):
        self.request_id = request_id
        self.client_id = client_id

    def serialize(self) -> str:
        if not Validator.validate_request_id(self.request_id):
            raise ValueError("Invalid request_id. Must be 7 lowercase letters (a-z)")

        if self.client_id is not None and not Validator.validate_client_id(self.client_id):
            raise ValueError("client_id must be alphanumeric")

        parts = [self.request_id]
        if self.client_id is not None:
            parts.append(self.client_id)

        return "|".join(parts) + "\n"
