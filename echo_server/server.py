"""TCP Echo Server implementation."""

import asyncio
import logging
from typing import NoReturn

from echo_server.request import Request
from echo_server.response import Response


logger = logging.getLogger(__name__)


class EchoServer:
    def __init__(self, host: str = "0.0.0.0", port: int = 8989) -> None:
        self.host = host
        self.port = port
        self._server: asyncio.AbstractServer | None = None
        self.sessions = {}


    async def handle_client(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        peer = writer.get_extra_info("peername")
        logger.info("New connection from %s", peer)
        logger.info("Sessions: %s", self.sessions)

        try:
            while True:
                data = await reader.readline()
                if not data:
                    break

                logger.info("Received %r from %s", data.decode(), peer)
                parsed_command = Request(data.decode())
                peer_str = f"{peer[0]}:{peer[1]}"
                logger.info("Peer str: %s", peer_str)

                if parsed_command.action == "SIGN_IN":
                    self.sessions[peer_str] = parsed_command.client_id
                    responseData = Response(request_id=parsed_command.request_id)
                    response = responseData.serialize(responseData)
                    logger.info("response: %s", response)

                    writer.write(response.encode())
                if parsed_command.action == "SIGN_OUT":
                    self.sessions[peer_str] = parsed_command.client_id
                    if peer_str in self.sessions:
                        del self.sessions[peer_str]
                    responseData = Response(request_id=parsed_command.request_id)
                    response = responseData.serialize(responseData)
                    writer.write(response.encode())
                elif parsed_command.action == "WHOAMI":
                    responseData = Response(request_id=parsed_command.request_id, client_id=self.sessions[peer_str] if peer_str in self.sessions else None)
                    response = responseData.serialize(responseData)
                    writer.write(response.encode())
                # logger.info("Responding %r to %s", response, peer)
                await writer.drain()

        except Exception as e:
            logger.error("Error handling client %s: %s", peer, e)
        finally:
            writer.close()
            if peer_str in self.sessions:
                del self.sessions[peer_str]
            await writer.wait_closed()
            logger.info("Connection closed from %s", peer)

    async def start(self) -> None:
        self._server = await asyncio.start_server(
            self.handle_client,
            self.host,
            self.port,
        )

        logger.info("Server starting on %s:%d", self.host, self.port)
        async with self._server:
            await self._server.serve_forever()

    async def stop(self) -> None:
        if self._server:
            self._server.close()
            await self._server.wait_closed()
            logger.info("Server stopped")


async def run_server() -> NoReturn:
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    server = EchoServer()
    try:
        await server.start()
    except KeyboardInterrupt:
        await server.stop()
    except Exception as e:
        logger.error("Server error: %s", e)
        raise