import asyncio
import datetime as dt

from minechat.conf import settings


def write_log(msg: str) -> None:
    """Write log message to file"""
    with open(settings.LOG_FILE_NAME, "a") as log_file:
        log_file.write(msg)


async def listen_chat():
    reader, writer = await asyncio.open_connection(settings.HOST, settings.PORT_OUT)

    while True:
        data = await reader.readline()
        timestamp_str = dt.datetime.now().strftime(settings.DATETIME_FMT)
        msg = f"[{timestamp_str}] {data.decode()}"
        print(msg)
        write_log(msg)

    print("Close the connection")
    writer.close()


async def send_to_chat():
    reader, writer = await asyncio.open_connection(settings.HOST, settings.PORT_IN)

    # authentication
    writer.write((settings.TOKEN + "\n").encode())

    while True:
        msg = input("Enter your message: ")
        if msg == "exit":
            break
        msg += "\n\n"
        writer.write(msg.encode())

    print("Close the connection")
    writer.close()


async def main():
    # await listen_chat()
    await send_to_chat()


if __name__ == "__main__":
    asyncio.run(main())
