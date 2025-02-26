"""TCP Echo Server implementation."""

import asyncio
import logging
from typing import NoReturn

logger = logging.getLogger(__name__)


class EchoServer:
    def __init__(self, host: str = "0.0.0.0", port: int = 8989) -> None:
        self.host = host
        self.port = port
        self._server: asyncio.AbstractServer | None = None

    async def handle_client(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        peer = writer.get_extra_info("peername")
        logger.info("New connection from %s", peer)

        try:
            while True:
                data = await reader.readline()
                if not data:
                    break

                logger.debug("Received %r from %s", data, peer)
                writer.write(data)
                await writer.drain()

        except Exception as e:
            logger.error("Error handling client %s: %s", peer, e)
        finally:
            writer.close()
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
