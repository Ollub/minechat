import argparse
import asyncio
import typing as tp

from minechat.cli import get_base_args
from minechat.client.client import Client
from minechat.conf import settings
from minechat.log import setup_log


async def main():
    setup_log()
    args = get_base_args()

    async with Client(
        host=args.host,
        port_in=args.port_in,
        port_out=args.port_out,
    ) as client:
        await client.consume()


if __name__ == "__main__":
    asyncio.run(main())
