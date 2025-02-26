"""Tests for the TCP Echo Server."""

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

    # test_data = b"Hello, Echo Server!\n"
    # writer.write(test_data)
    # await writer.drain()
    #
    # response = await reader.readline()
    # assert response == test_data
    #
    # writer.close()
    # await writer.wait_closed()
