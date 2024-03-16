from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from bot.utils.crud import get_wb_product_cards_for_user
from bot.utils.text import generate_product_info_from_card
from config import BotCmdsEnum
from db.session import get_session

NO_CARDS_TXT = 'Для вас пока не сохранено ни одной карточки товара.'
YOUR_CARDS_TXT = 'Вот ваши последние {num_cards} карточки товаров:\n'

router = Router()


@router.message(
    StateFilter('*'),
    Command(BotCmdsEnum.GET_INFO_FROM_DB.command)
)
async def get_info_from_db(message: Message, state: FSMContext):
    await state.clear()
    tg_user_id = message.from_user.id
    async with get_session() as session:
        product_cards = await get_wb_product_cards_for_user(
            session=session, tg_user_id=tg_user_id
        )
    if not product_cards:
        await message.answer(
            text=NO_CARDS_TXT, reply_markup=ReplyKeyboardRemove()
        )
        return
    num_cards = len(product_cards)
    text = YOUR_CARDS_TXT.format(num_cards=num_cards)
    for card in product_cards:
        text += '\n\n' + generate_product_info_from_card(card, with_dt=True)
    await message.answer(text=text, reply_markup=ReplyKeyboardRemove())
