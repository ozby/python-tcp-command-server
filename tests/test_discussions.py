from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, patch

import pytest

from server.commands.command import CommandContext
from server.commands.discussion_commands import (
    CreateDiscussionCommand,
    CreateReplyCommand,
    GetDiscussionCommand,
    ListDiscussionsCommand,
)
from server.services.session_service import SessionService
from server.validation import Validator

TEST_PEER_ID = "127.0.0.1:89899"



@pytest.fixture(autouse=True)
async def client_id() -> AsyncGenerator[str, None]:
    client_id = "tester_client_1"
    await SessionService().set(TEST_PEER_ID, client_id)
    yield client_id

def test_create_discussion_validates_params() -> None:
    context = CommandContext("abcdefg", ["ref.123", "test comment"], TEST_PEER_ID)
    CreateDiscussionCommand(
        context
    )  # Should not raise - validation in __init__

    with pytest.raises(ValueError, match="action requires two parameters"):
        CreateDiscussionCommand(CommandContext("abcdefg", [], TEST_PEER_ID))

    with pytest.raises(ValueError, match="action requires two parameters"):
        CreateDiscussionCommand(CommandContext("abcdefg", ["ref.123"], TEST_PEER_ID))

    with pytest.raises(
        ValueError, match="reference must be period-delimited alphanumeric"
    ):
        CreateDiscussionCommand(
            CommandContext("abcdefg", ["invalid!", "test"], TEST_PEER_ID)
        )


async def test_create_discussion_executes(client_id: str) -> None:
    discussion_id = "abcdzzz"
    with patch(
        "server.commands.discussion_commands.DiscussionService"
    ) as mock_service_class:
        mock_service = mock_service_class.return_value
        # Create an async mock for the async create_discussion method
        mock_service.create_discussion = AsyncMock(return_value=discussion_id)

        context = CommandContext("abcdefg", ["ref.123", "test comment"], TEST_PEER_ID)
        command = CreateDiscussionCommand(context)
        # The mock will automatically be used because we're patching at the module level
        result = (await command.execute()).rstrip("\n")
        parts = result.split("|")
        assert len(parts) == 2
        assert parts[0] == "abcdefg"
        assert parts[1] == discussion_id
        assert Validator.validate_request_id(parts[1])

        mock_service.create_discussion.assert_called_once_with(
            "ref.123", "test comment", client_id
        )


async def test_create_reply_executes() -> None:
    created = CreateDiscussionCommand(
        CommandContext("abcdefg", ["ref.123", "test comment"], TEST_PEER_ID)
    )
    created_discussion_id = (await created.execute()).strip("\n").split("|")[1]

    reply = CreateReplyCommand(
        CommandContext(
            "abcdefg", [created_discussion_id, "test reply yooo"], TEST_PEER_ID
        )
    )
    replied = await reply.execute()
    print(f"replied: {replied}")

    returned_discussion = GetDiscussionCommand(
        CommandContext("abcdefg", [created_discussion_id], TEST_PEER_ID)
    )
    returned = await returned_discussion.execute()
    assert '"' not in returned
    print(f"returned discussion after reply: {returned}")


async def test_create_reply_executes_with_comma() -> None:
    created = CreateDiscussionCommand(
        CommandContext("abcdefg", ["ref.123", "test comment"], TEST_PEER_ID)
    )
    created_discussion_id = (await created.execute()).strip("\n").split("|")[1]

    reply = CreateReplyCommand(
        CommandContext(
            "abcdefg", [created_discussion_id, "test reply, yooo"], TEST_PEER_ID
        )
    )
    replied = await reply.execute()
    print(f"replied: {replied}")

    returned_discussion = GetDiscussionCommand(
        CommandContext("abcdefg", [created_discussion_id], TEST_PEER_ID)
    )
    returned = await returned_discussion.execute()
    assert '"' in returned
    print(f"returned discussion after reply: {returned}")


async def test_get_discussion_executes(client_id: str) -> None:
    created = CreateDiscussionCommand(
        CommandContext("abcdefg", ["ref.123", "test comment"], TEST_PEER_ID)
    )
    created_discussion_id = (await created.execute()).strip("\n").split("|")[1]
    print(f"created_discussion_id: {created_discussion_id}")

    returned_discussion = GetDiscussionCommand(
        CommandContext("abcdefg", [created_discussion_id], TEST_PEER_ID)
    )
    returned = await returned_discussion.execute()
    assert (
        returned
        == f"abcdefg|{created_discussion_id}|ref.123|({client_id}|test comment)\n"
    )


def test_create_reply_validates_params() -> None:
    context = CommandContext("abcdefg", ["disc123", "test reply"], TEST_PEER_ID)
    CreateReplyCommand(context)  # Should not raise - validation in __init__

    with pytest.raises(ValueError, match="action requires two parameters"):
        CreateReplyCommand(CommandContext("abcdefg", [], TEST_PEER_ID))

    with pytest.raises(ValueError, match="action requires two parameters"):
        CreateReplyCommand(CommandContext("abcdefg", ["disc123"], TEST_PEER_ID))


def test_get_discussion_validates_params() -> None:
    context = CommandContext("abcdefg", ["disc123"], TEST_PEER_ID)
    GetDiscussionCommand(context)  # Should not raise - validation in __init__

    with pytest.raises(ValueError, match="action requires one parameter"):
        GetDiscussionCommand(CommandContext("abcdefg", [], TEST_PEER_ID))

    with pytest.raises(ValueError, match="action requires one parameter"):
        GetDiscussionCommand(
            CommandContext("abcdefg", ["disc123", "extra"], TEST_PEER_ID)
        )


async def test_list_discussion_validates_params() -> None:
    created = CreateDiscussionCommand(
        CommandContext("abcdefg", ["ndgdojs.15s", "test comment"], TEST_PEER_ID)
    )
    created_discussion_id = (await created.execute()).strip("\n").split("|")[1]

    reply = CreateReplyCommand(
        CommandContext(
            "replyaa",
            [created_discussion_id, "I love this video. What did you use to make it?"],
            TEST_PEER_ID,
        )
    )
    await reply.execute()

    reply = CreateReplyCommand(
        CommandContext(
            "replybb",
            [
                created_discussion_id,
                'I used something called "Synthesia", it\'s pretty cool!',
            ],
            TEST_PEER_ID,
        )
    )
    await reply.execute()

    created = CreateDiscussionCommand(
        CommandContext("zzzzccs", ["asdasds.15s", "test comment"], TEST_PEER_ID)
    )
    created_discussion_id = (await created.execute()).strip("\n").split("|")[1]

    reply = CreateReplyCommand(
        CommandContext("replyaa", [created_discussion_id, "sadsdsadas"], TEST_PEER_ID)
    )
    await reply.execute()

    reply = CreateReplyCommand(
        CommandContext("replybb", [created_discussion_id, "pdskfdsjfds"], TEST_PEER_ID)
    )
    await reply.execute()


async def test_list_discussion_executes() -> None:
    command = ListDiscussionsCommand(CommandContext("abcdefg", [], TEST_PEER_ID))
    result = await command.execute()
    print(f"result: {result}")
