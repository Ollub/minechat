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
        "--port_out",
        help="Порт для прослушивания чата",
        required=False,
        default=None,
    )
    parser.add_argument(
        "--port_in",
        help="Порт для отправки сообщений в чат",
        required=False,
        default=None,
    )
    return parser.parse_args().__dict__


class Settings(BaseSettings):
    """App settings."""

    HOST: str = ""
    PORT_OUT: int = 5000
    PORT_IN: int = 5050
    # TOKEN: str = "8dce7dee-e78a-11eb-8c47-0242ac110002"
    TOKEN: str = ""
    TOKEN_STORAGE_FILE_PATH = ".token"
    DATETIME_FMT = "%Y-%m-%d %H:%M:%S"
    LOG_FILE_NAME = "debug.log"

    class Config:  # noqa: WPS431 nested class
        """Config for settings."""

        case_sensitive = True

    def __init__(self):
        super().__init__()
        self.populate_with_cli_args()
        self.check_configuration()

    def check_configuration(self):
        if not (self.HOST or self.PORT_OUT):
            raise ConfigurationError("host or port not configured")

    def populate_with_cli_args(self):
        cli_args = get_args()
        for argname, value in cli_args.items():
            if value is None:
                continue
            setattr(self, argname.upper(), value)


settings = Settings()
