import asyncio
import logging
import typing as tp
from functools import wraps
from pathlib import Path

from minechat.conf import settings
from minechat.exceptions import RetryException

logger = logging.getLogger()


def get_token_from_file() -> str:
    """Read token from file."""
    token = ""
    token_file = Path(settings.TOKEN_STORAGE_FILE_PATH)
    if token_file.exists():
        with open(token_file, "r") as file:
            token = file.readline()
    return token


def save_token_to_file(token: str) -> None:
    with open(settings.TOKEN_STORAGE_FILE_PATH, "w") as file:
        file.write(token)


def async_retry(*exceptions, attempts: int = 3, wait_time_seconds: float = 5):
    """Async retry decorator."""

    exceptions_list = exceptions + (RetryException,)

    def factory(func: tp.Callable):  # type: ignore
        @wraps(func)
        async def decorator(*args, **kwargs):
            exception: tp.Union[
                Exception,
                tp.Type[Exception],
            ] = RetryException  # will be overriden
            for _ in range(attempts):
                try:
                    res = await func(*args, **kwargs)
                except exceptions_list as exc:
                    exception = exc
                    await asyncio.sleep(wait_time_seconds)
                    logger.debug(f"Retry attempt. Exception: {str(exc)}")
                    continue
                break
            else:
                # raise caught exception
                raise exception
            return res

        return decorator

    return factory
