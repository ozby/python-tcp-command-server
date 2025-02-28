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
        peer_info = writer.get_extra_info("peername")
        peer_id = f"{peer_info[0]}:{peer_info[1]}"
        logger.info("New connection from %s", peer_id)

        try:
            while True:
                data = await reader.readline()
                if not data:
                    break

                logger.info("Received %r from %s", data.decode(), peer_id)
                parsed_command = Request.from_line(data.decode(), peer_id)
                logger.info("parsed_command: %s", parsed_command)

                action_man = ActionFactory.execute_action(
                    parsed_command.action,
                    parsed_command.request_id,
                    parsed_command.params,
                    peer_id,
                )
                response_from_action = action_man.execute()
                logger.info("response: %s", response_from_action)

                writer.write(response_from_action.encode())
                await writer.drain()

        except Exception as e:
            writer.write(str(e).encode())
            logger.error("Error handling client %s: %s", peer_id, e)
        finally:
            writer.close()
            SessionService().delete(peer_id)
            await writer.wait_closed()
            logger.info("Connection closed from %s", peer_id)

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
