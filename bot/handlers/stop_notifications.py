from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import KeyboardButton, Message, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from bot.utils.crud import (
    get_product_ids_subscribed_by_user, delete_notification_subscription,
    delete_all_subscriptions_for_user,
)
from config import BotCmdsEnum, config
from db.session import get_session

NO_PROD_SUBSCRIBED_TXT = 'У вас нет активных подписок.'
PROMPT_TO_CHOOSE_TXT = (
    'Перед вами артикулы товаров, на которые вы подписаны.\n'
    'Выберете тот, от которого хотите отписаться.'
)
NO_SUCH_SUB_TXT = 'Вы не подписаны на товар с артикулом {product_id}.'
PROD_UNSUB_TEXT = (
    'Вы отписались от товара с артикулом {product_id}.'
    'Хотите отписаться от ещё какого-нибудь товара?'
)
ALL_PROD_UNSUB_TEXT = 'Вы отписались от всех товаров.'
UNSUB_CANCEL_TEXT = 'Вы отменили отписку от товаров.'
CANCEL_BUTTON_TEXT = 'Отмена'
UNSUB_ALL_BUTTON_TEXT = 'Отписаться от всех товаров'

router = Router()


class StopNotificationsStates(StatesGroup):
    waiting_for_user_choice = State()


@router.message(
    StateFilter('*'),
    Command(BotCmdsEnum.STOP_NOTIFICATIONS.command)
)
async def start_conversation(message: Message, state: FSMContext):
    await state.clear()
    async with get_session() as session:
        product_ids = await get_product_ids_subscribed_by_user(
            session=session, tg_user_id=message.from_user.id
        )
    if not product_ids:
        await message.answer(
            text=NO_PROD_SUBSCRIBED_TXT, reply_markup=ReplyKeyboardRemove()
        )
        return await state.clear()
    await state.update_data(product_ids=product_ids)
    keyboard = _get_keyboard_for_product_ids(product_ids)
    text = PROMPT_TO_CHOOSE_TXT
    await message.answer(
        text, reply_markup=keyboard.as_markup(resize_keyboard=True)
    )
    await state.set_state(StopNotificationsStates.waiting_for_user_choice)


@router.message(
    StateFilter(StopNotificationsStates.waiting_for_user_choice),
    F.text.func(
        lambda text: text.replace(' ', '').isdigit()
    )
)
async def product_id_recieved(message: Message, state: FSMContext):
    data = await state.get_data()
    product_ids = data.get('product_ids')
    product_id = int(message.text.replace(' ', ''))
    if product_id not in product_ids:
        await message.answer(
            NO_SUCH_SUB_TXT.format(product_id=product_id)
        )
        return
    tg_user_id = message.from_user.id
    async with get_session() as session:
        await delete_notification_subscription(
            session=session, tg_user_id=tg_user_id, wb_product_id=product_id
        )
    product_ids.remove(product_id)
    await state.update_data(product_ids=product_ids)
    if not product_ids:
        text = ALL_PROD_UNSUB_TEXT
        await message.answer(text, reply_markup=ReplyKeyboardRemove())
        return await state.clear()
    text = PROD_UNSUB_TEXT.format(product_id=product_id)
    keyboard = _get_keyboard_for_product_ids(product_ids)
    await message.answer(text, reply_markup=keyboard.as_markup())


@router.message(
    StateFilter(StopNotificationsStates.waiting_for_user_choice),
    F.text.lower() == UNSUB_ALL_BUTTON_TEXT.lower()
)
async def unsubscribe_from_all_products(message: Message, state: FSMContext):
    tg_user_id = message.from_user.id
    async with get_session() as session:
        await delete_all_subscriptions_for_user(session, tg_user_id)
    await message.answer(
        ALL_PROD_UNSUB_TEXT, reply_markup=ReplyKeyboardRemove()
    )
    await state.clear()


@router.message(
    StateFilter(StopNotificationsStates.waiting_for_user_choice),
    F.text.lower() == CANCEL_BUTTON_TEXT.lower()
)
async def cancel_conversation(message: Message, state: FSMContext):
    await message.answer(
        UNSUB_CANCEL_TEXT, reply_markup=ReplyKeyboardRemove()
    )
    await state.clear()


def _get_keyboard_for_product_ids(
        product_ids: list[int]
) -> ReplyKeyboardBuilder:
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(KeyboardButton(text=CANCEL_BUTTON_TEXT))
    for product_id in product_ids:
        keyboard.add(KeyboardButton(text=str(product_id)))
    if len(product_ids) > 1:
        keyboard.add(KeyboardButton(text=UNSUB_ALL_BUTTON_TEXT))
    keyboard.adjust(config.buttons_in_row)
    return keyboard
