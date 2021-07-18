import argparse
import os
import typing as tp

from pydantic import BaseSettings

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class ConfigurationError(Exception):
    """Application configuration error exception."""


def get_args() -> tp.Dict[str, tp.Any]:
    """Config argparse parser and read args."""
    parser = argparse.ArgumentParser(
        description="Скрипт для подключения к подпольному чату",
    )
    parser.add_argument(
        "--host",
        help="IP адрес или доменное имя чата",
        required=False,
        default=None,
    )
    parser.add_argument(
        "--port",
        help="Порт",
        required=False,
        default=None,
    )
    return parser.parse_args().__dict__


class Settings(BaseSettings):
    """App settings."""

    HOST: str = ""
    PORT: int = 5000
    DATETIME_FMT = "%d.%m.%y %H:%M"
    LOG_FILE_NAME = "../log.txt"

    class Config:  # noqa: WPS431 nested class
        """Config for settings."""

        case_sensitive = True

    def __init__(self):
        super().__init__()
        self.populate_with_cli_args()
        self.check_configuration()

    def check_configuration(self):
        if not (self.HOST or self.PORT):
            raise ConfigurationError("host or port not configured")

    def populate_with_cli_args(self):
        cli_args = get_args()
        for argname, value in cli_args.items():
            if value is None:
                continue
            setattr(self, argname.upper(), value)


settings = Settings()
