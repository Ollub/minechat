import asyncio
import logging

from minechat.conf import settings
from minechat.log import setup_log

logger = logging.getLogger(__name__)


class Client:
    """Minechat client."""

    _reader: asyncio.StreamReader
    _writer: asyncio.StreamWriter

    async def connect(self):
        self._reader = await self.get_reader()
        self._writer = await self.get_writer()

    async def get_reader(self) -> asyncio.StreamReader:
        reader, writer = await asyncio.open_connection(settings.HOST, settings.PORT_OUT)
        return reader

    async def get_writer(self) -> asyncio.StreamWriter:
        reader, writer = await asyncio.open_connection(settings.HOST, settings.PORT_IN)
        return writer

    async def authenticate(self):
        msg = settings.TOKEN + "\n"
        await self._send_msg(msg)
        logger.debug("Authenticated")

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
    await cli.consume()
    await cli.close()


if __name__ == "__main__":
    asyncio.run(main())
