import asyncio
import json
import logging
from pathlib import Path

from minechat.conf import settings
from minechat.log import setup_log
from minechat.utils import get_token_from_file, save_token_to_file

logger = logging.getLogger(__name__)


class ClientException(Exception):
    """Minechat client base exception."""


class BadTokenException(ClientException):
    """Invalid token provided exception."""


class Client:
    """Minechat client."""

    _reader: asyncio.StreamReader
    _writer: asyncio.StreamWriter
    _auth_reader: asyncio.StreamReader
    _is_authenticated: bool = False

    async def connect(self):
        self._reader, _ = await asyncio.open_connection(
            settings.HOST,
            settings.PORT_OUT,
        )
        self._auth_reader, self._writer = await asyncio.open_connection(
            settings.HOST,
            settings.PORT_IN,
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
        await self._send_msg(msg, drain=True)

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
        await self._send_msg("\n", drain=True)
        # receive enter nickname message
        data = await self._auth_reader.readline()
        logger.debug(f"Message from server: {data.decode()}")

        username = input("Enter your nickname: ")
        logger.debug(f"Register user: {username}")
        await self._send_msg(username + "\n", drain=True)

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
            await self._send_msg(msg)

    async def close(self):
        self._writer.close()
        logger.debug("Connection closed")

    async def _fetch_msg(self) -> str:
        data = await self._reader.readline()
        return data.decode()

    async def _send_msg(self, msg: str, drain=False) -> None:
        self._writer.write(msg.encode())
        if drain:
            await self._writer.drain()

    @property
    def token(self) -> str:
        """Get token from settings or from file."""
        return settings.TOKEN or get_token_from_file()


async def main():
    setup_log()
    cli = Client()
    await cli.connect()
    await cli.authenticate()
    await cli.produce()
    await cli.close()


if __name__ == "__main__":
    asyncio.run(main())
