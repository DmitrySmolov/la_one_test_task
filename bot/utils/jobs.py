from aiogram import Bot

from bot.utils import crud
from bot.utils.api import get_product_card_from_api
from bot.utils.text import generate_product_info_from_card
from db.session import get_session

YOUR_NOTIFICATION_TXT = (
    'Оповещение по вашей подписке на товар с Wildberries: \n\n'
)


async def send_product_notifications_for_subscribers(bot: Bot):
    """Отправляет уведомления о товарах подписчикам."""
    async with get_session() as session:
        subscribed_product_ids = (
            await crud.get_distinct_product_ids_from_subscriptions(
                session=session
            )
        )
        pydantic_product_cards = []
        for id in subscribed_product_ids:
            product_card = await get_product_card_from_api(product_id=id)
            if product_card:
                pydantic_product_cards.append(product_card)
                await crud.create_wb_product_card(
                    session=session, **product_card.for_db_card_model_dump()
                )
        for card in pydantic_product_cards:
            user_ids = await crud.get_user_ids_subscribed_to_product(
                session=session, product_id=card.id
            )
            for id in user_ids:
                text = (YOUR_NOTIFICATION_TXT)
                text += generate_product_info_from_card(card)
                await bot.send_message(chat_id=id, text=text)
