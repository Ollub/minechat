import asyncio
import json
import logging
import socket
import typing as tp
from contextlib import asynccontextmanager

from pydantic.main import BaseModel

from minechat.client.exceptions import AuthenticationError
from minechat.client.typings import RegistrationResult
from minechat.utils import async_retry

logger = logging.getLogger(__name__)

TOKEN_KEY = "account_hash"


class Connection(BaseModel):
    reader: asyncio.StreamReader
    writer: asyncio.StreamWriter
    authorization_passed: bool = False

    class Config:
        arbitrary_types_allowed = True


@asynccontextmanager
async def connect_tcp_socket(host: str, port: int) -> Connection:

    connection = await _init_tcp_connection(host, port)
    logger.debug(f"Connection established. host: {host}, port: {port}")
    try:
        yield connection
    finally:
        connection.writer.close()
        logger.debug("Connection closed")


@async_retry(socket.gaierror)
async def _init_tcp_connection(host: str, port: int) -> Connection:
    reader, writer = await asyncio.open_connection(host=host, port=port)
    return Connection(reader=reader, writer=writer)


async def send_msg(conn: Connection, msg: str, drain: bool = True) -> None:
    """Send message via tcp connection."""
    conn.writer.write(_preprocess_msg(msg))
    if drain:
        await conn.writer.drain()
    logger.debug(f"Message sent: {msg}")


def _preprocess_msg(msg: str) -> bytes:
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


async def fetch_msg(conn: Connection) -> str:
    data = await conn.reader.readline()
    msg = data.decode()
    logger.debug(f"Got message: {msg}")
    return msg


async def fetch_json(conn: Connection) -> tp.Optional[tp.Dict[str, str]]:
    return json.loads(await fetch_msg(conn))


async def listen_server(conn: Connection) -> tp.AsyncIterator[str]:
    while True:
        msg = await fetch_msg(conn)
        yield msg


async def authenticate(conn: Connection, token: str):
    if conn.authorization_passed:
        logger.debug("Already authenticated")
        return

    # skip greeting
    msg = await fetch_msg(conn)
    logger.debug(f"Greeting mgs: {msg}")

    logger.debug("Authentication attempt")
    await send_msg(conn, token)
    authentication_result = await fetch_json(conn)
    logger.debug(f"Authentication result: {authentication_result}")

    if authentication_result is None:
        error_msg = "Provided token is invalid!"
        logger.warning(error_msg)
        raise AuthenticationError(error_msg)

    conn.authorization_passed = True
    logger.info("Successfully authenticated")


async def register(conn: Connection, username: str) -> RegistrationResult:
    """Register new user."""
    logger.debug("Registering new user")

    # skip greeting
    msg = await fetch_msg(conn)
    logger.debug(f"Greeting mgs: {msg}")

    logger.debug("Send empty message to skip authentication")
    await send_msg(conn, "")

    # skip "enter nickname" message
    msg = await fetch_msg(conn)
    logger.debug(f"Message from server: {msg}")

    logger.debug(f"Registering user: {username}")
    await send_msg(conn, username)

    registration_result = RegistrationResult(
        username=username, **(await fetch_json(conn))
    )
    logger.info(
        f"Registered user {username} with nickname {registration_result.nickname}",
    )

    return registration_result
