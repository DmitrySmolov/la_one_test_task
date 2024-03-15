from enum import Enum

from aiogram.types import BotCommand
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr

ENV_FILE = '.env'
ENCODING = 'utf-8'


class Settings(BaseSettings):
    """
    Класс настроек приложения.
    """
    bot_token: SecretStr
    database_url: SecretStr
    wb_api_url: SecretStr
    scheduler_interval: int = 5
    timezone: str = 'Europe/Moscow'
    buttons_in_row: int = 4
    product_cards_limit: int = 5
    user_dt_format: str = '%d.%m.%Y %H:%M:%S'

    model_config = SettingsConfigDict(
        env_file=ENV_FILE, env_file_encoding=ENCODING, extra='ignore'
    )


class BotCmdsEnum(Enum):
    """
    Енум для хранения команд бота.
    """
    GET_PRODUCT_INFO = (
        'get_product_info',
        'Получить информацию по товару'
    )
    STOP_NOTIFICATIONS = (
        'stop_notifications',
        'Остановить уведомления'
    )
    GET_INFO_FROM_DB = (
        'get_info_from_db',
        'Получить информацию из БД'
    )

    @property
    def command(self) -> str:
        """Возвращает команду для бота."""
        return self.value[0]

    @property
    def description(self) -> str:
        """Возвращает описание команды."""
        return self.value[1]

    @classmethod
    def get_commands(cls) -> list[BotCommand]:
        """
        Возвращает список объектов BotCommand для метода бота
        `set_my_commands`.
        """
        return [
            BotCommand(
                command=cmd.command,
                description=cmd.description
            ) for cmd in cls
        ]


config = Settings()
