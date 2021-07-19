import logging.config

from minechat.conf import settings

logger_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "std_format": {
            "format": "[{asctime}] {message}",
            "datefmt": settings.DATETIME_FMT,
            "style": "{",
        },
        "file_format": {
            "format": "[{asctime}] - {levelname} - {name} - {message}",
            "datefmt": settings.DATETIME_FMT,
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "std_format",
        },
        "file": {
            "class": "logging.FileHandler",
            "level": "DEBUG",
            "filename": settings.LOG_FILE_NAME,
            "formatter": "file_format",
        },
    },
    "loggers": {
        "root": {
            "level": "DEBUG",
            "handlers": ["console", "file"],
        },
    },
}

logging.config.dictConfig(logger_config)


def setup_log() -> None:
    """Empty function for importing log config."""
