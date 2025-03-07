"""TCP Echo Server implementation."""

import asyncio
import logging
from datetime import datetime
from typing import TypedDict

from server.commands.command_context import CommandContext
from server.commands.command_factory import CommandFactory
from server.di import Container

logger = logging.getLogger(__name__)


class NotificationDocument(TypedDict):
    discussion_id: str
    recipient_id: str
    sender_id: str
    notification_type: str  # NotificationType.value
    created_at: datetime


class Server:
    _server: asyncio.AbstractServer

    def __init__(
        self,
        container: Container,
        host: str = "0.0.0.0",
        port: int = 8989,
    ) -> None:
        self.host = host
        self.port = port
        self._notification_task: asyncio.Task[None] | None = None
        self._peer_writers: dict[str, asyncio.StreamWriter] = {}

        self.container = container
        self.session_service = self.container.session_service()
        self.notification_service = self.container.notification_service()
        self.mongo_client = self.container.mongo_client()
        self.db = self.mongo_client

        # Set up notification service callback
        self.notification_service.set_send_callback(self._send_notification_to_peer)

    async def _send_notification_to_peer(self, recipient_id: str, message: str) -> None:
        """Send a notification message to a specific peer."""
        peer_id = await self._get_peer_id(recipient_id)
        if not peer_id:
            return

        peer_writer = self._peer_writers[peer_id]
        logger.info(f"Notification sending to {peer_id}: {message}")
        peer_writer.write(message.encode())
        logger.info(f"Notification sent to {peer_id}")
        await peer_writer.drain()

    async def _get_peer_id(self, recipient_id: str) -> str | None:
        """Get peer_id for a recipient, handling offline cases."""
        peer_id = await self.session_service.get_by_user_id(recipient_id)
        if peer_id is None:
            logger.info(f"User is offline: {recipient_id}")
            return None

        if peer_id not in self._peer_writers:
            logger.info(f"User is offline: {peer_id}")
            return None

        return peer_id

    async def _send_to_peer(self, peer_id: str, message: str) -> None:
        """Send a message to a specific peer if they are connected."""
        peer_writer = self._peer_writers.get(peer_id)
        if peer_writer is None:
            logger.info("User is offline: %s", peer_id)
            return

        logger.info("Sending message to %s: %s", peer_id, message)
        peer_writer.write(message.encode())
        await peer_writer.drain()
        logger.info("Message sent to %s", peer_id)

    async def handle_client(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        peer_info = writer.get_extra_info("peername")
        peer_id = f"{peer_info[0]}:{peer_info[1]}"
        logger.info("New connection from %s", peer_id)
        try:
            self._peer_writers[peer_id] = writer

            while True:
                data = await reader.readline()
                if not data:
                    break

                context = CommandContext.from_line(
                    self.container, data.decode(), peer_id
                )
                command = CommandFactory.create_command(context)
                response = await command.execute()
                logger.info("response: %s", response)

                writer.write(response.encode())
                await writer.drain()

        except Exception as e:
            writer.write(str(e).encode())
            logger.error("Error handling client %s: %s", peer_id, e)
        finally:
            self._peer_writers.pop(peer_id, None)
            writer.close()
            await self.session_service.delete(peer_id)
            await writer.wait_closed()
            logger.info("Connection closed from %s", peer_id)

    async def start(self) -> None:
        self._server = await asyncio.start_server(
            self.handle_client,
            self.host,
            self.port,
        )

        self._notification_task = asyncio.create_task(
            self.notification_service.watch_notifications()
        )

        # For testing, the container might not have a config attribute
        db_name = self.container.config.db_name
        logger.info(f"Using database: {db_name}")

        logger.info("Server starting on %s:%d", self.host, self.port)
        async with self._server:
            await self._server.serve_forever()

    async def stop(self) -> None:
        logger.info("Stopping server...")

        if self._server:
            self._server.close()
            await self._server.wait_closed()

        self.mongo_client.close()


async def run_server() -> None:
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    server = Server(container=Container())
    try:
        await server.start()
    except KeyboardInterrupt:
        await server.stop()
    except Exception as e:
        logger.error("Server error: %s", e)
        await server.stop()
        raise
