import asyncio
import logging

from aiogram import Bot, Dispatcher

from bot.handlers.product_info import router
from config import BotCmdsEnum, config

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.bot_token.get_secret_value())

dp = Dispatcher()

dp.include_router(router)


async def main():
    await bot.delete_my_commands()
    await bot.set_my_commands(
        commands=BotCmdsEnum.get_commands()
    )
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
