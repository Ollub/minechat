import argparse
import typing as tp

from pydantic import BaseModel


class BaseCliArguments(BaseModel):
    host: tp.Optional[str]
    port_in: tp.Optional[int]
    port_out: tp.Optional[int]


class ProducerCliArguments(BaseCliArguments):
    username: tp.Optional[str]
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
        "--msg",
        help="Сообщение для отправки",
        required=True,
        default=None,
    )
    return parser


def get_producer_arguments() -> ProducerCliArguments:
    parser = configure_producer_parser()
    return ProducerCliArguments(**parser.parse_args().__dict__)
