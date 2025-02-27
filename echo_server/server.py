"""TCP Echo Server implementation."""

import asyncio
import logging

from echo_server.actions.action_factory import ActionFactory
from echo_server.request import Request
from echo_server.session import SessionAuth

logger = logging.getLogger(__name__)


class EchoServer:
    def __init__(self, host: str = "0.0.0.0", port: int = 8989) -> None:
        self.host = host
        self.port = port
        self._server: asyncio.AbstractServer | None = None

    async def handle_client(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        self.session_auth = SessionAuth(writer)

        peer = writer.get_extra_info("peername")
        peer_str = f"{peer[0]}:{peer[1]}"
        logger.info("Peer str: %s", peer_str)

        logger.info("New connection from %s", peer)

        try:
            while True:
                data = await reader.readline()
                if not data:
                    break

                logger.info("Received %r from %s", data.decode(), peer)
                parsed_command = Request.from_line(data.decode())
                logger.info("parsed_command: %s", parsed_command)

                action_man = ActionFactory.create_action(
                    parsed_command.action,
                    parsed_command.request_id,
                    parsed_command.params,
                    self.session_auth,
                )
                response_from_action = action_man.execute()
                logger.info("response: %s", response_from_action)

                writer.write(response_from_action.encode())
                await writer.drain()

        except Exception as e:
            logger.error("Error handling client %s: %s", peer, e)
        finally:
            writer.close()
            self.session_auth.delete()
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


async def run_server() -> None:
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
