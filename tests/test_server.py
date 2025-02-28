"""Integration Test for the TCP Echo Server."""

import asyncio
from collections.abc import AsyncGenerator

import pytest

from server import Server


@pytest.fixture
async def server() -> AsyncGenerator[Server, None]:
    server = Server(port=0)
    task = asyncio.create_task(server.start())
    await asyncio.sleep(0.1)
    yield server
    await server.stop()
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


@pytest.mark.asyncio
async def test_server_echo(server) -> None:
    port = server._server.sockets[0].getsockname()[1]
    reader, writer = await asyncio.open_connection("127.0.0.1", port)

    test_actions = ["hijklmn|SIGN_IN|testuser", "abcdefg|WHOAMI", "opqrstu|SIGN_OUT"]
    expected_responses = ["hijklmn\n", "abcdefg|testuser\n", "opqrstu\n"]

    for i, action in enumerate(test_actions):
        writer.write((action + "\n").encode())
        await writer.drain()

        response = await reader.readline()

        assert response.decode().replace("_id", "") == expected_responses[i]

    writer.close()
