import asyncio
import logging

from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot.handlers.get_product_info import router as product_info_router
from bot.handlers.stop_notifications import (
    router as stop_notifications_router
)
from bot.handlers.database_info import router as database_info_router
from bot.utils.jobs import send_product_notifications_for_subscribers
from config import BotCmdsEnum, config

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.bot_token.get_secret_value())

dp = Dispatcher()
dp.include_routers(
    product_info_router,
    stop_notifications_router,
    database_info_router,
)


async def main():
    scheduler = AsyncIOScheduler(timezone=config.timezone)
    scheduler.add_job(
        func=send_product_notifications_for_subscribers,
        trigger='interval',
        minutes=config.scheduler_interval,
        kwargs={'bot': bot}
    )
    scheduler.start()
    await bot.delete_my_commands()
    await bot.set_my_commands(
        commands=BotCmdsEnum.get_commands()
    )
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
