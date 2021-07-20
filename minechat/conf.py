import os

from pydantic import BaseSettings

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Settings(BaseSettings):
    """App settings."""

    HOST: str = ""
    PORT_OUT: int = 5000
    PORT_IN: int = 5050
    TOKEN: str = ""
    TOKEN_STORAGE_FILE_PATH = os.path.join(PROJECT_DIR, "minechat", ".token")
    DATETIME_FMT = "%Y-%m-%d %H:%M:%S"
    LOG_FILE_NAME = "debug.log"

    class Config:  # noqa: WPS431 nested class
        """Config for settings."""

        case_sensitive = True


settings = Settings()
