from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from config import BotCmdsEnum


router = Router()


@router.message(Command(BotCmdsEnum.GET_PRODUCT_INFO.command))
async def test_handler(message: Message):
    await message.answer(
        'Лёд тронулся, господа присяжные заседатели! 🧣'
    )
