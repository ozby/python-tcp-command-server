from re import compile


class Validator:
    REQUEST_ID_PATTERN = compile(r"^[a-z]{7}$")
    CLIENT_ID_PATTERN = compile(r"^[a-zA-Z0-9]+$")

    @classmethod
    def validate_request_id(cls, request_id: str) -> bool:
        return bool(cls.REQUEST_ID_PATTERN.match(request_id))

    @classmethod
    def validate_client_id(cls, client_id: str) -> bool:
        return bool(cls.CLIENT_ID_PATTERN.match(client_id))
