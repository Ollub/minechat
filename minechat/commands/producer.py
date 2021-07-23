import asyncio
import logging
import logging.config
import socket

from minechat.cli import get_producer_arguments
from minechat.client.client import AuthenticationError, MinechatPublisher
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

    async with MinechatPublisher(
        host=args.host,
        port=args.port or settings.PORT_IN,
    ) as client:
        if token:
            await client.authenticate(token)
            await client.send_msg(args.msg)
            print("Message sent")
        else:
            token = await client.register(args.username)
            save_token_to_file(token)

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
