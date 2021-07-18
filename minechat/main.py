import asyncio
import datetime as dt

from minechat.conf import settings


def write_log(msg: str) -> None:
    """Write log message to file"""
    with open(settings.LOG_FILE_NAME, "a") as log_file:
        log_file.write(msg)


class Client:
    """Minechat client."""

    _reader: asyncio.StreamReader
    _writer: asyncio.StreamWriter

    def __init__(self):
        asyncio.ensure_future(self.connect())

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
        print("Authenticated")

    async def consume(self):
        while True:
            msg = await self._fetch_msg()
            print(msg)
            write_log(msg)

    async def produce(self):
        while True:
            msg = input("Enter your message: ")
            if msg == "exit":
                break
            msg += "\n\n"
            await self._send_msg(msg)

    async def close(self):
        print("Close the connection")
        self._writer.close()

    async def _fetch_msg(self) -> str:
        data = await self._reader.readline()
        timestamp_str = dt.datetime.now().strftime(settings.DATETIME_FMT)
        msg = f"[{timestamp_str}] {data.decode()}"
        return msg

    async def _send_msg(self, msg: str) -> None:
        self._writer.write(msg.encode())


async def main():
    cli = Client()
    # TODO: replace sleep with smth
    await asyncio.sleep(1)  # wait for connection
    await cli.authenticate()
    await cli.produce()
    await cli.close()


if __name__ == "__main__":
    asyncio.run(main())
