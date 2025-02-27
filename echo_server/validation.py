from re import compile


class Validator:
    REQUEST_ID_PATTERN = compile(r"^[a-z]{7}$")
    ALPHANUMERIC_PATTERN = compile(r"^[a-zA-Z0-9]+$")

    @classmethod
    def validate_request_id(cls, request_id: str) -> bool:
        return bool(cls.REQUEST_ID_PATTERN.match(request_id))

    @classmethod
    def validate_client_id(cls, client_id: str) -> bool:
        return bool(cls.ALPHANUMERIC_PATTERN.match(client_id))

    @classmethod
    def validate_reference(cls, reference: str) -> bool:
        # Split the reference by periods and validate each part is alphanumeric
        parts = reference.split(".")
        return all(bool(cls.ALPHANUMERIC_PATTERN.match(part)) for part in parts)
