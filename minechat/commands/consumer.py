import asyncio
import datetime as dt

from minechat.cli import get_base_args
from minechat.client.client import MinechatClient
from minechat.conf import settings
from minechat.log import setup_log


def format_msg(msg: str) -> str:
    now = dt.datetime.now()
    return f"[{now.strftime(settings.DATETIME_FMT)}] {msg}".strip("\n")


async def main():
    setup_log()
    args = get_base_args()

    async with MinechatClient(
        host=args.host,
        port=args.port or settings.PORT_OUT,
    ) as client:
        async for msg in client.listen():
            print(format_msg(msg))


if __name__ == "__main__":
    asyncio.run(main())
