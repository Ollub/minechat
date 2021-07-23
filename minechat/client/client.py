import asyncio
import json
import logging
import socket
import typing as tp

from minechat.utils import async_retry

logger = logging.getLogger(__name__)

TOKEN_KEY = "account_hash"


class BaseClientException(Exception):
    """Base client exception class."""

    error_msg: str

    def __init__(self, error_msg: str):
        self.error_msg = error_msg


class ClientNotConfigured(BaseClientException):
    """Client configuration error."""


class AuthenticationError(BaseClientException):
    """Client not authenticated."""


class BaseTcpClient:

    username: tp.Optional[str]
    host: str
    port: int
    _reader: asyncio.StreamReader
    _writer: asyncio.StreamWriter

    def __init__(
        self,
        host: tp.Optional[str] = None,
        port: tp.Optional[int] = None,
    ):
        self.host = host
        self.port = port

    async def __aenter__(self):
        """Create connection."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close connection."""
        await self.close()

    def check_configuration(self):
        if not self.host:
            logger.error("Host was not provided for client initialization")
            raise ClientNotConfigured("Host is missing")
        if not self.port:
            logger.error("Port was not provided for client initialization")
            raise ClientNotConfigured("Port is missing")

    @async_retry(socket.gaierror)
    async def connect(self):
        self.check_configuration()
        self._reader, self._writer = await asyncio.open_connection(
            self.host,
            self.port,
        )
        logger.debug(f"Connection established to {self.host}:{self.port}")

    async def close(self):
        self._writer.close()
        logger.debug("Connection closed")

    async def fetch_msg(self) -> str:
        data = await self._reader.readline()
        msg = data.decode()
        logger.debug(f"Got message: {msg}")
        return msg

    async def listen(self) -> str:
        while True:
            msg = await self.fetch_msg()
            yield msg

    async def send_msg(self, msg: str, drain=True) -> None:
        await self._send(msg, drain)

    async def _send(self, msg: str, drain=True) -> None:
        self._writer.write(self._preprocess_msg(msg))
        if drain:
            await self._writer.drain()
        logger.debug(f"Message sent: {msg}")

    def _preprocess_msg(self, msg: str) -> bytes:
        """Prepare message for sending to socket."""


class MinechatClient(BaseTcpClient):
    """Client for connecting to minecraft chat via TCP."""

    def _preprocess_msg(self, msg: str) -> bytes:
        """
        Prepare message for sending to chat.

        Server interpret new line symbols ('\n')
        as the end of the message
        that is why we remove those symbols from message.

        Finally we add control symbol `\n\n` to send message.
        """
        msg = msg.replace("\n", " ")
        msg += "\n\n"
        return msg.encode()


class MinechatPublisher(MinechatClient):
    """
    Client for publishing messages to minecraft chat.

    Authentication should be passed before pushing messages to chat.
    """

    is_authenticated: bool = False

    async def send_msg(self, msg: str, drain=True) -> None:
        if not self.is_authenticated:
            logger.debug("Trying to send message with unauthenticated client.")
            raise AuthenticationError(
                "Client should be authenticated before publishing.",
            )
        await super().send_msg(msg, drain)

    async def authenticate(self, token: str):
        if self.is_authenticated:
            logger.debug("Client already authenticated.")
            return

        # skip greeting
        msg = await self.fetch_msg()
        logger.debug(f"Greeting mgs: {msg}")

        logger.debug("Authentication attempt")
        msg = token + "\n"
        await self._send(msg)
        authentication_result = json.loads(await self.fetch_msg())
        logger.debug(f"Authentication result: {authentication_result}")

        if authentication_result is None:
            error_msg = "Provided token is invalid!"
            logger.warning(error_msg)
            raise AuthenticationError(error_msg)

        self.is_authenticated = True
        logger.info("Successfully authenticated")

    async def register(self, username: str) -> str:
        """
        Register new user.

        @return: token
        """
        logger.debug("Registering new user")

        # skip greeting
        msg = await self.fetch_msg()
        logger.debug(f"Greeting mgs: {msg}")

        logger.debug("Send empty message to skip authentication")
        await self._send("")

        # skip "enter nickname" message
        msg = await self.fetch_msg()
        logger.debug(f"Message from server: {msg}")

        logger.debug(f"Registering user: {username}")
        await self._send(username)

        # receive creation result and extract token from it
        # result = await self.fetch_msg()
        creation_result = json.loads(await self.fetch_msg())
        logger.info(f"User {username} created")

        return creation_result["account_hash"]
