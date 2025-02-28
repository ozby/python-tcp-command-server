"""TCP Echo Server implementation."""

import asyncio
import logging

from server.commands.command_factory import CommandFactory
from server.di import Container
from server.request import Request

logger = logging.getLogger(__name__)


class Server:
    def __init__(
        self,
        container: Container,
        host: str = "0.0.0.0",
        port: int = 8989,
    ) -> None:
        self.host = host
        self.port = port
        self._server: asyncio.AbstractServer | None = None
        self._notification_task: asyncio.Task[None] | None = None
        self._peer_writers: dict[str, asyncio.StreamWriter] = {}
        self._running = False

        from server import get_container

        self.container = container
        self.session_service = self.container.session_service()

    async def _watch_notifications(self) -> None:
        """Single watcher for all notifications"""
        try:
            logger.info("Starting notification watcher")
            mongo_client = self.container.mongo_client()
            db_name = str(self.container.config["db_name"])

            if not db_name:
                logger.warning("Empty database name, notification watcher not started")
                return

            db = mongo_client[db_name]
            collection = db.notifications

            pipeline = [{"$match": {"operationType": "insert"}}]

            async with collection.watch(pipeline) as stream:
                while self._running:
                    try:
                        change = await stream.try_next()
                        if change is None:
                            await asyncio.sleep(0.1)
                            continue

                        notification = change["fullDocument"]
                        logger.info("Received notification: %s", notification)
                        recipient_id = notification["recipient_id"]
                        peer_id = await self.session_service.get_by_user_id(
                            recipient_id
                        )
                        if peer_id is not None:
                            peer_writer = self._peer_writers.get(peer_id)
                            if peer_writer is None:
                                logger.info(f"User is offline: {peer_id}")
                                continue
                            message = (
                                f"DISCUSSION_UPDATED|{notification['discussion_id']}\n"
                            )
                            logger.info(f"Notification sending to {peer_id}: {message}")
                            peer_writer.write(message.encode())
                            logger.info(f"Notification sent to {peer_id}")
                            await peer_writer.drain()
                        else:
                            logger.info(f"No peer ID found for user: {recipient_id}")
                    except Exception as e:
                        if not self._running:
                            break
                        logger.error(f"Error processing notification: {e}")
                        await asyncio.sleep(1)
        except Exception as e:
            if self._running:
                logger.error(f"Notification watcher error: {e}")

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

                logger.info("Received %r from %s", data.decode(), peer_id)
                parsed_command = Request.from_line(data.decode(), peer_id)
                logger.info("parsed_command: %s", parsed_command)

                command = CommandFactory.create_command(
                    parsed_command.action,
                    parsed_command.request_id,
                    parsed_command.params,
                    peer_id,
                )
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

        self._running = True
        self._notification_task = asyncio.create_task(self._watch_notifications())

        logger.info("Server starting on %s:%d", self.host, self.port)
        async with self._server:
            await self._server.serve_forever()

    async def stop(self) -> None:
        logger.info("Stopping server...")
        self._running = False

        if self._server:
            self._server.close()
            await self._server.wait_closed()
        
        if self._notification_task:
            self._notification_task.cancel()
            
        for _, writer in list(self._peer_writers.items()):
            writer.close()
            
        self._peer_writers.clear()
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
        await server.stop()
        raise
