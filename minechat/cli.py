import argparse
import typing as tp

from pydantic import BaseModel


class BaseCliArguments(BaseModel):
    host: tp.Optional[str]
    port: tp.Optional[int]


class ProducerCliArguments(BaseCliArguments):
    username: tp.Optional[str]
    token: tp.Optional[str]
    msg: str


def configure_base_parser() -> argparse.ArgumentParser:
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
    return parser


def get_base_args() -> BaseCliArguments:
    parser = configure_base_parser()
    return BaseCliArguments(**parser.parse_args().__dict__)


def configure_producer_parser() -> argparse.ArgumentParser:
    parser = configure_base_parser()
    parser.add_argument(
        "--username",
        help="Имя пользователя",
        required=False,
        default=None,
    )
    parser.add_argument(
        "--token",
        help="Токен, полученый при регистрации в чате",
        required=False,
        default=None,
    )
    parser.add_argument(
        "--msg",
        help="Сообщение для отправки",
        required=True,
        default=None,
    )
    return parser


def get_producer_arguments() -> ProducerCliArguments:
    parser = configure_producer_parser()
    return ProducerCliArguments(**parser.parse_args().__dict__)
