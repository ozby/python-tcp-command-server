from dataclasses import dataclass

from server.db.entities.reply import Reply


@dataclass
class Discussion:
    discussion_id: str
    reference_prefix: str
    reference: str
    client_id: str
    replies: list[Reply]
