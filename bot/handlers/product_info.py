from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

from bot.utils.api import get_product_card_from_api
from bot.utils.crud import subscribe_user_to_product
from bot.utils.text import generate_product_info_from_card
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
        'Введите артикул товара с Wildberries для получения информации о нем.'
    )
    await state.set_state(ConversationStates.waiting_for_product_id)


@router.message(
    ConversationStates.waiting_for_product_id,
    F.text
)
async def product_id_recieved(message: Message, state: FSMContext):
    await _delete_last_answer_inline_keyboard(message, state)
    message_text = ''.join(message.text.strip().split())
    if not message_text.isdigit():
        await message.answer(
            'Артикул должен содержать только цифры.'
        )
        return
    product_id = int(message_text)
    product_card = await get_product_card_from_api(product_id)
    if not product_card:
        await message.answer('Товар не найден.')
        return

    await state.update_data(current_card=product_card)

    text = generate_product_info_from_card(product_card)
    text += (
        '\nНажмите на кнопку ниже, чтобы подписаться на обновления или '
        'введите новый артикул.'
    )
    keyboard = InlineKeyboardBuilder().row(
        InlineKeyboardButton(text='подписаться', callback_data='subscribe')
    )
    bot_answer = await message.answer(
        text=text,
        reply_markup=keyboard.as_markup()
    )
    answer_message_id = bot_answer.message_id
    await state.update_data(answer_message_id=answer_message_id)


@router.callback_query(F.data == 'subscribe')
async def subscribe(callback: CallbackQuery, state: FSMContext):
    message = callback.message
    await _delete_last_answer_inline_keyboard(message, state)
    state_data = await state.get_data()
    product_card = state_data.get('current_card')
    tg_user_id = message.chat.id
    wb_product_id = product_card.id
    try:
        await subscribe_user_to_product(tg_user_id, product_card)
    except ValueError:
        text = 'Вы уже подписаны на информацию по товару с артикулом '
        text += str(wb_product_id)
        await message.answer(text)
        return
    await message.answer(
        f'Вы подписаны на оповещения по товару с артикулом {wb_product_id}.'
    )
    await state.clear()


async def _delete_last_answer_inline_keyboard(
    message: Message, state: FSMContext
):
    state_data = await state.get_data()
    if (
        answer_id := state_data.get('answer_message_id', None)
    ):
        bot = message.bot
        await bot.edit_message_reply_markup(
            chat_id=message.chat.id,
            message_id=answer_id,
            reply_markup=None
        )
