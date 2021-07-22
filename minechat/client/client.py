import asyncio
import json
import logging
import typing as tp

from minechat.conf import settings
from minechat.utils import get_token_from_file, save_token_to_file

logger = logging.getLogger(__name__)


class BaseClientException(Exception):
    """Base client exception class."""


class ClientNotConfigured(BaseClientException):
    """Client configuration error."""


class Client:
    """Minechat client."""

    username: tp.Optional[str]
    host: str
    port_in: int
    port_out: int
    _reader: asyncio.StreamReader
    _writer: asyncio.StreamWriter
    _auth_reader: asyncio.StreamReader
    _is_authenticated: bool = False

    def __init__(
        self,
        username: tp.Optional[str] = None,
        host: tp.Optional[str] = None,
        port_out: tp.Optional[int] = None,
        port_in: tp.Optional[int] = None,
    ):
        self.username = username
        self.host = host or settings.HOST
        self.port_in = port_in or settings.PORT_IN
        self.port_out = port_out or settings.PORT_OUT

    async def __aenter__(self):
        """Create connection."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close connection."""
        await self.close()

    def check_configuration(self):
        if not self.host:
            raise ClientNotConfigured("Missing host argument data")
        if not (self.port_in and self.port_out):
            raise ClientNotConfigured("Missing ports arguments data")

    async def connect(self):
        self.check_configuration()
        self._reader, _ = await asyncio.open_connection(
            self.host,
            self.port_out,
        )
        self._auth_reader, self._writer = await asyncio.open_connection(
            self.host,
            self.port_in,
        )

    async def authenticate(self):
        # skip greeting
        msg = await self._auth_reader.readline()
        logger.debug(f"Greeting mgs: {msg.decode()}")

        if self.token:
            await self._process_authentication()
        else:
            await self._register_new_user()

    async def _process_authentication(self) -> None:
        # msg = await self._auth_reader.readline()
        # logger.debug(f"Greeting mgs: {msg.decode()}")
        msg = self.token + "\n"
        await self.send_msg(msg, drain=True)

        logger.debug("Getting authentication result")
        authentication_result = json.loads(await self._auth_reader.readline())
        if authentication_result is None:
            logger.warning("Provided token is invalid!")
        else:
            logger.info("Successfully authenticated")
            self._is_authenticated = True

    async def _register_new_user(self):
        logger.debug("Registering new user")

        logger.debug("Send empty message to skip authentication")
        await self.send_msg("\n", drain=True)
        # receive enter nickname message
        data = await self._auth_reader.readline()
        logger.debug(f"Message from server: {data.decode()}")

        username = self.username or input("Enter your nickname: ")
        logger.debug(f"Register user: {username}")
        await self.send_msg(username + "\n", drain=True)

        # receive creation result and save token
        creation_result = json.loads(await self._auth_reader.readline())
        logger.debug(f"Creation result: {creation_result}")
        save_token_to_file(creation_result["account_hash"])
        logger.info("User created")

    async def consume(self):
        while True:
            msg = await self._fetch_msg()
            logger.info(msg)

    async def produce(self):
        while True:
            msg = input("Enter your message: ")
            if msg == "exit":
                break
            # server interpret new line symbols ('\n')
            # as end of message
            # that is why we remove those symbols from message
            msg = msg.replace("\n", " ")
            msg += "\n\n"
            await self.send_msg(msg)

    async def close(self):
        self._writer.close()
        logger.debug("Connection closed")

    async def _fetch_msg(self) -> str:
        data = await self._reader.readline()
        return data.decode()

    async def send_msg(self, msg: str, drain=False) -> None:
        self._writer.write(self._preprocess_msg(msg))
        if drain:
            await self._writer.drain()
        logger.debug(f"Message sent: {msg}")

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

    @property
    def token(self) -> str:
        """Get token from settings or from file."""
        return settings.TOKEN or get_token_from_file()
