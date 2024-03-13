from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

from bot.utils.api import get_product_card_from_api
from config import BotCmdsEnum

router = Router()


class ConversationStates(StatesGroup):
    waiting_for_product_id = State()


@router.message(
    StateFilter(None),
    Command(BotCmdsEnum.GET_PRODUCT_INFO.command)
)
async def start_conversation(message: Message, state: FSMContext):
    await message.answer(
        'Введите id товара для получения информации о нем.'
    )
    await state.set_state(ConversationStates.waiting_for_product_id)


@router.message(
    ConversationStates.waiting_for_product_id,
    F.text
)
async def product_id_recieved(message: Message):
    if not message.text.isdigit():
        await message.answer('Id должен быть числом.')
        return
    product_id = int(message.text)
    product_card = await get_product_card_from_api(product_id)
    if not product_card:
        await message.answer('Товар не найден.')
        return
    user_data = product_card.for_user_model_dump()
    text = ''
    for key, value in user_data.items():
        text += f'{key}: {value}\n'
    keyboard = InlineKeyboardBuilder().row(
        InlineKeyboardButton(text='подписаться', callback_data='subscribe')
    )
    await message.answer(
        text=text,
        reply_markup=keyboard.as_markup()
    )


@router.callback_query(F.data == 'subscribe')
async def subscribe(callback: CallbackQuery):
    await callback.message.answer('Здесь будет реализована подписка на товар.')
