from server.validation import Validator


class Response:
    def __init__(self, request_id: str, params: list[str] | None = None):
        if params is None:
            params = []
        self.request_id = request_id
        self.params = params

    def serialize(self) -> str:
        if not Validator.validate_request_id(self.request_id):
            raise ValueError("Invalid request_id. Must be 7 lowercase letters (a-z)")

        parts = [self.request_id]
        if len(self.params) > 0:
            parts.extend(self.params)

        return "|".join(parts) + "\n"
    
    def serialize_list(self) -> str:
        if not Validator.validate_request_id(self.request_id):
            raise ValueError("Invalid request_id. Must be 7 lowercase letters (a-z)")

        return self.request_id + "|(" + ",".join(self.params) + ")\n"
