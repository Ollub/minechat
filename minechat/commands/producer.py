import asyncio

from minechat.cli import get_producer_arguments
from minechat.client.client import Client
from minechat.log import setup_log


async def main():
    setup_log()
    args = get_producer_arguments()

    async with Client(
        host=args.host,
        port_in=args.port_in,
        port_out=args.port_out,
        username=args.username,
    ) as client:
        await client.authenticate()
        await client.send_msg(args.msg)


if __name__ == "__main__":
    asyncio.run(main())
