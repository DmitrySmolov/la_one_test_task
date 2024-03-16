from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

from bot.utils.api import get_product_card_from_api
from bot.utils.crud import (
    get_notification_subscription, subscribe_user_to_product
)
from bot.utils.text import generate_product_info_from_card
from config import BotCmdsEnum, config
from db.session import get_session

PROMPT_ENTER_PRODUCT_ID_TXT = (
    'Введите артикул товара с Wildberries для получения информации о нем '
    f'каждые {config.scheduler_interval} минут.'
)
DIGITS_ONLY_TXT = 'Артикул должен содержать только цифры.'
PRODUCT_NOT_FOUND_TXT = 'Товар не найден.'
PROMPT_SUBSCRIBE_OR_NEXT_ID_TXT = (
    '\n\nНажмите на кнопку ниже, чтобы подписаться на обновления или '
    'введите новый артикул.'
)
PROMPT_NEXT_ID_TXT = (
    '\n\nДля получения новой информации введите артикул товара.'
)
SUBSCRIBE_CALLBACK_DATA = 'subscribe'
SUBSCRIBE_KEYBOARD = InlineKeyboardBuilder().row(InlineKeyboardButton(
    text='подписаться', callback_data=SUBSCRIBE_CALLBACK_DATA
))
SUBSCRIBED_ALREADY_TXT = (
    'Вы уже подписаны на информацию по товару с артикулом {wb_product_id}.'
)
SUBSCRIPTION_SUCCESS_TXT = (
    'Вы подписаны на информацию по товару с артикулом {wb_product_id}.'
    '\n\n Если захотите подписаться на что-то ещё, снова вызовите команду '
    f'/{BotCmdsEnum.GET_PRODUCT_INFO.command} в меню бота. \n\n'
    'Для отписки от уведомлений используйте команду '
    f'/{BotCmdsEnum.STOP_NOTIFICATIONS.command} в меню бота.'
)

router = Router()


class GetProductInfoStates(StatesGroup):
    waiting_for_product_id = State()


@router.message(
    StateFilter('*'),
    Command(BotCmdsEnum.GET_PRODUCT_INFO.command)
)
async def start_conversation(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text=PROMPT_ENTER_PRODUCT_ID_TXT,
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(GetProductInfoStates.waiting_for_product_id)


@router.message(
    GetProductInfoStates.waiting_for_product_id,
    F.text & ~F.text.startswith('/')
)
async def product_id_recieved(message: Message, state: FSMContext):
    await _delete_last_answer_inline_keyboard(message, state)
    message_text = message.text.replace(' ', '')
    if not message_text.isdigit():
        await message.answer(DIGITS_ONLY_TXT)
        return
    product_id = int(message_text)
    product_card = await get_product_card_from_api(product_id)
    if not product_card:
        await message.answer(PRODUCT_NOT_FOUND_TXT)
        return

    await state.update_data(current_card=product_card)

    text = generate_product_info_from_card(product_card)
    async with get_session() as session:
        tg_user_id = message.chat.id
        subscription = await get_notification_subscription(
            session, tg_user_id, product_id
        )
    if not subscription:
        text += PROMPT_SUBSCRIBE_OR_NEXT_ID_TXT
        keyboard = SUBSCRIBE_KEYBOARD
        bot_answer = await message.answer(
            text=text,
            reply_markup=keyboard.as_markup()
        )
        return await state.update_data(
            answer_message_id=bot_answer.message_id
        )
    text += PROMPT_NEXT_ID_TXT
    bot_answer = await message.answer(text=text)
    await state.update_data(answer_message_id=bot_answer.message_id)


@router.callback_query(F.data == SUBSCRIBE_CALLBACK_DATA)
async def subscribe(callback: CallbackQuery, state: FSMContext):
    message = callback.message
    await _delete_last_answer_inline_keyboard(message, state)
    state_data = await state.get_data()
    product_card = state_data.get('current_card')
    tg_user_id = message.chat.id
    wb_product_id = product_card.id
    async with get_session() as session:
        try:
            await subscribe_user_to_product(session, tg_user_id, product_card)
        except ValueError:
            text = SUBSCRIBED_ALREADY_TXT.format(wb_product_id=wb_product_id)
            await message.answer(text)
            return
    await message.answer(
        SUBSCRIPTION_SUCCESS_TXT.format(wb_product_id=wb_product_id)
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
        try:
            await bot.edit_message_reply_markup(
                chat_id=message.chat.id,
                message_id=answer_id,
                reply_markup=None
            )
        except TelegramBadRequest:
            return
