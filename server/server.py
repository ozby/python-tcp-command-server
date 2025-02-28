"""TCP Echo Server implementation."""

import asyncio
import logging

import motor.motor_asyncio

from server.commands.command_factory import CommandFactory
from server.db.mongo_client import mongo_client
from server.request import Request
from server.services.session_service import SessionService

logger = logging.getLogger(__name__)


class Server:
    def __init__(self, host: str = "0.0.0.0", port: int = 8989) -> None:
        self.host = host
        self.port = port
        self._server: asyncio.AbstractServer | None = None
        self._notification_task: asyncio.Task | None = None
        self._peer_writers: dict[str, asyncio.StreamWriter] = {}
        self._running = False

    async def _watch_notifications(self) -> None:
        """Single watcher for all notifications"""
        try:
            logger.info("Starting notification watcher")
            client = motor.motor_asyncio.AsyncIOMotorClient(
                "mongodb://localhost:27017/?replicaSet=rs0"
            )
            collection = client.synthesia_db.notifications
            async with collection.watch([{'$match': {'operationType': 'insert'}}]) as stream:
                while self._running:
                    try:
                        change = await stream.try_next()
                        if change is None:
                            # No new changes, wait a bit before trying again
                            await asyncio.sleep(0.1)
                            continue
                            
                        notification = change['fullDocument']
                        logger.info("Received notification: %s", notification)
                        recipient_id = notification['recipient_id']
                        peer_id = SessionService().get_by_user_id(recipient_id)
                        peer_writer = self._peer_writers.get(peer_id)
                        if (peer_writer is None):
                            logger.info(f"User is offline: {peer_id}")
                            continue
                        message = f"DISCUSSION_UPDATED|{notification['discussion_id']}\n"
                        logger.info(f"Notification sending to {peer_id}: {message}")
                        peer_writer.write(message.encode())
                        logger.info(f"Notification sent to {peer_id}")
                        await peer_writer.drain()
                    except Exception as e:
                        if not self._running:
                            break
                        logger.error(f"Error processing notification: {e}")
                        await asyncio.sleep(1)  # Wait before retrying
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
                response = command.execute()
                logger.info("response: %s", response)

                writer.write(response.encode())
                await writer.drain()

        except Exception as e:
            writer.write(str(e).encode())
            logger.error("Error handling client %s: %s", peer_id, e)
        finally:
            self._peer_writers.pop(peer_id, None)
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
        
        self._running = True
        self._notification_task = asyncio.create_task(self._watch_notifications())

        logger.info("Server starting on %s:%d", self.host, self.port)
        async with self._server:
            await self._server.serve_forever()

    async def stop(self) -> None:
        logger.info("Stopping server...")
        self._running = False
        
        # Stop accepting new connections
        if self._server:
            self._server.close()
            await self._server.wait_closed()
        
        # Cancel notification task
        if self._notification_task:
            self._notification_task.cancel()
            try:
                await self._notification_task
            except asyncio.CancelledError:
                pass
        
        # Close all client connections
        for writer in self._peer_writers.values():
            writer.close()
            try:
                await writer.wait_closed()
            except Exception as e:
                logger.error(f"Error closing client connection: {e}")
        
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
