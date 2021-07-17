import asyncio
import datetime as dt

HOST = "minechat.dvmn.org"
PORT = 5000
DATETIME_FMT = "%d.%m.%y %H:%M"
LOG_FILE_NAME = "../log.txt"


def write_log(msg: str) -> None:
    """Write log message to file"""
    with open(LOG_FILE_NAME, "a") as log_file:
        log_file.write(msg)


async def tcp_echo_client(message):
    reader, writer = await asyncio.open_connection(HOST, PORT)

    while True:
        data = await reader.readline()
        timestamp_str = dt.datetime.now().strftime(DATETIME_FMT)
        msg = f"[{timestamp_str}] {data.decode()}"
        print(msg)
        write_log(msg)

    print("Close the connection")
    writer.close()


asyncio.run(tcp_echo_client("Hello World!"))

if __name__ == "__main__":
    asyncio.run(tcp_echo_client("Hello World!"))
