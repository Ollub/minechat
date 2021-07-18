import asyncio
import datetime as dt

from minechat.conf import settings


def write_log(msg: str) -> None:
    """Write log message to file"""
    with open(settings.LOG_FILE_NAME, "a") as log_file:
        log_file.write(msg)


async def tcp_client():
    reader, writer = await asyncio.open_connection(settings.HOST, settings.PORT)

    while True:
        data = await reader.readline()
        timestamp_str = dt.datetime.now().strftime(settings.DATETIME_FMT)
        msg = f"[{timestamp_str}] {data.decode()}"
        print(msg)
        write_log(msg)

    print("Close the connection")
    writer.close()


if __name__ == "__main__":
    asyncio.run(tcp_client())
