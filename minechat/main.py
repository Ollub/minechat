import asyncio
import json
import logging

from minechat.conf import settings
from minechat.log import setup_log

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
        msg = settings.TOKEN + "\n"
        await self._send_msg(msg)

        logger.debug("Getting authentication result")
        authentication_result = json.loads(await self._auth_reader.readline())
        if authentication_result is None:
            logger.warning("Provided token is invalid!")
        else:
            logger.info("Successfully authenticated")

    async def consume(self):
        while True:
            msg = await self._fetch_msg()
            logger.info(msg)

    async def produce(self):
        while True:
            msg = input("Enter your message: ")
            if msg == "exit":
                break
            msg += "\n\n"
            await self._send_msg(msg)

    async def close(self):
        self._writer.close()
        logger.debug("Connection closed")

    async def _fetch_msg(self) -> str:
        data = await self._reader.readline()
        return data.decode()

    async def _send_msg(self, msg: str) -> None:
        self._writer.write(msg.encode())


async def main():
    setup_log()
    cli = Client()
    await cli.connect()
    await cli.authenticate()
    # await cli.consume()
    await cli.close()


if __name__ == "__main__":
    asyncio.run(main())
