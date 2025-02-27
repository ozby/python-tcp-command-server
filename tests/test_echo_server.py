"""Integration Test for the TCP Echo Server."""

import asyncio

import pytest

from echo_server import EchoServer


@pytest.fixture
async def echo_server():
    server = EchoServer(port=0)
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
async def test_echo_server_echo(echo_server):
    port = echo_server._server.sockets[0].getsockname()[1]
    reader, writer = await asyncio.open_connection("127.0.0.1", port)

    test_actions = ["hijklmn|SIGN_IN|testuser", "abcdefg|WHOAMI", "opqrstu|SIGN_OUT"]
    expected_responses = ["hijklmn\n", "abcdefg|testuser\n", "opqrstu\n"]

    for i, action in enumerate(test_actions):
        writer.write((action + "\n").encode())
        await writer.drain()

        response = await reader.readline()

        assert response.decode() == expected_responses[i]

    writer.close()
