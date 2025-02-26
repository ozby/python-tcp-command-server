from dataclasses import dataclass

from echo_server.validation import Validator


@dataclass
class Response:
    request_id: str
    client_id: str | None = None


class ResponseGenerator:
    @classmethod
    def serialize(cls, response: Response) -> str:
        if not Validator.validate_request_id(response.request_id):
            raise ValueError("Invalid request_id. Must be 7 lowercase letters (a-z)")

        if response.client_id is not None and not Validator.validate_client_id(response.client_id):
            raise ValueError("client_id must be alphanumeric")

        parts = [response.request_id]
        if response.client_id is not None:
            parts.append(response.client_id)

        return "|".join(parts) 