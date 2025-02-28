class Reply:
    def __init__(self, client_id: str, comment: str) -> None:
        self.client_id = client_id
        self.comment = comment


class Discussion:
    def __init__(self, discussion_id: str, reference: str) -> None:
        self.discussion_id = discussion_id
        self.reference = reference
        self.replies: list[Reply] = []
