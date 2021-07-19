from pathlib import Path

from minechat.conf import settings


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
