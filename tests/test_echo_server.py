"""Tests for the TCP Echo Server."""

import asyncio
import logging

import pytest

from echo_server import EchoServer
from echo_server.response import Response


# @pytest.fixture
# async def echo_server():
#     server = EchoServer(port=0)
#     task = asyncio.create_task(server.start())
#     await asyncio.sleep(0.1)
#     yield server
#     await server.stop()
#     task.cancel()
#     try:
#         await task
#     except asyncio.CancelledError:
#         pass


@pytest.mark.asyncio
async def test_echo_server_echo():
    # port = echo_server._server.sockets[0].getsockname()[1]
    reader, writer = await asyncio.open_connection("127.0.0.1", 8989)

    test_commands = [
        "hijklmn|SIGN_IN|testuser",
        "abcdefg|WHOAMI",
        "opqrstu|SIGN_OUT"
    ]
    expected_responses = [
        "hijklmn\n",
        "abcdefg|testuser\n",
        "opqrstu\n"
    ]

    for i, command in enumerate(test_commands):
        writer.write((command + "\n").encode())
        await writer.drain()

        response = await reader.readline()

        assert response.decode() == expected_responses[i]

    writer.close()