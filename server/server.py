"""TCP Echo Server implementation."""

import asyncio
import logging

from server.actions.action_factory import ActionFactory
from server.request import Request
from server.services.session_service import SessionService

logger = logging.getLogger(__name__)


class Server:
    def __init__(self, host: str = "0.0.0.0", port: int = 8989) -> None:
        self.host = host
        self.port = port
        self._server: asyncio.AbstractServer | None = None

    async def handle_client(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        peerInfo = writer.get_extra_info("peername")
        peer_str = f"{peerInfo[0]}:{peerInfo[1]}"
        logger.info("New connection from %s", peer_str)

        try:
            while True:
                data = await reader.readline()
                if not data:
                    break

                logger.info("Received %r from %s", data.decode(), peer_str)
                parsed_command = Request.from_line(data.decode(), peer_str)
                logger.info("parsed_command: %s", parsed_command)

                action_man = ActionFactory.execute_action(
                    parsed_command.action,
                    parsed_command.request_id,
                    parsed_command.params,
                    peer_str,
                )
                response_from_action = action_man.execute()
                logger.info("response: %s", response_from_action)

                writer.write(response_from_action.encode())
                await writer.drain()

        except Exception as e:
            writer.write(str(e).encode())
            logger.error("Error handling client %s: %s", peer_str, e)
        finally:
            writer.close()
            SessionService().delete(peer_str)
            await writer.wait_closed()
            logger.info("Connection closed from %s", peer_str)

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

    server = Server()
    try:
        await server.start()
    except KeyboardInterrupt:
        await server.stop()
    except Exception as e:
        logger.error("Server error: %s", e)
        raise
