import asyncio
import logging
import logging.config
import socket

from minechat import client
from minechat.cli import get_producer_arguments
from minechat.client.exceptions import AuthenticationError
from minechat.conf import settings
from minechat.log import logger_config
from minechat.utils import get_token_from_file, save_token_to_file

logger = logging.getLogger(__name__)


async def producer():
    """
    Authenticate in chat and send message to chat.

    If token not passed new user will be registered.
    """
    args = get_producer_arguments()

    token = args.token or settings.TOKEN or get_token_from_file()
    if not (token or args.username):
        logger.warning("Script can not be started: username or token not provided")
        print("Please provide token or username for registration.")
        return

    async with client.connect_tcp_socket(
        host=args.host,
        port=args.port or settings.PORT_IN,
    ) as conn:
        if token:
            await client.authenticate(conn, token)
            await client.send_msg(conn, args.msg)
            print("Message sent")
        else:
            result = await client.register(conn, args.username)
            save_token_to_file(result.token)

        print("Bye!")


async def main():
    logging.config.dictConfig(logger_config)
    try:
        await producer()
    except AuthenticationError as err:
        print(err.error_msg)
    except socket.gaierror:
        print("Connection error. Please try to run script later.")


if __name__ == "__main__":
    asyncio.run(main())
