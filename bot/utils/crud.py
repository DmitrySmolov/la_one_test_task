from sqlalchemy import select

from bot.utils.entities import PydanticProductCard
from db.session import AsyncSessionLocal
from db.models import NotificationSubscription, WBProduct, WBProductCard


async def create_wb_product(**kwargs) -> None:
    """Создаёт новую запись в таблице товаров."""
    async with AsyncSessionLocal() as session:
        async with session.begin():
            wb_product = WBProduct(**kwargs)
            session.add(wb_product)
            await session.commit()


async def check_wb_product_exists(product_id: int) -> bool:
    """Проверяет, существует ли товар с указанным артикулом."""
    async with AsyncSessionLocal() as session:
        async with session.begin():
            query = select(WBProduct).where(WBProduct.id == product_id)
            result = await session.execute(query)
            product = result.scalar()
            return bool(product)


async def create_notification_subscription(
    tg_user_id: int, wb_product_id: int
) -> None:
    """Создаёт новую запись в таблице подписок."""
    async with AsyncSessionLocal() as session:
        async with session.begin():
            subscription = NotificationSubscription(
                tg_user_id=tg_user_id, wb_product_id=wb_product_id
            )
            session.add(subscription)
            await session.commit()


async def delete_notification_subscription(
    tg_user_id: int, wb_product_id: int
) -> None:
    """Удаляет запись из таблицы подписок."""
    async with AsyncSessionLocal() as session:
        async with session.begin():
            query = (
                select(NotificationSubscription)
                .where(
                    NotificationSubscription.tg_user_id == tg_user_id,
                    NotificationSubscription.wb_product_id == wb_product_id,
                )
            )
            result = await session.execute(query)
            subscription = result.scalar()
            await session.delete(subscription)
            await session.commit()


async def check_subscription_exists(
        tg_user_id: int, wb_product_id: int
) -> bool:
    """Проверяет, существует ли подписка на товар."""
    async with AsyncSessionLocal() as session:
        async with session.begin():
            query = (
                select(NotificationSubscription)
                .where(
                    NotificationSubscription.tg_user_id == tg_user_id,
                    NotificationSubscription.wb_product_id == wb_product_id,
                )
            )
            result = await session.execute(query)
            subscription = result.scalar()
            return bool(subscription)


async def subscribe_user_to_product(
    tg_user_id: int, wb_product: PydanticProductCard
) -> None:
    """Подписывает пользователя на товар."""
    wb_product_id = wb_product.id
    if not await check_wb_product_exists(wb_product_id):
        await create_wb_product(
            **wb_product.for_db_product_model_dump()
        )
    if await check_subscription_exists(tg_user_id, wb_product_id):
        raise ValueError('Подписка уже существует.')
    await create_notification_subscription(tg_user_id, wb_product_id)


async def get_distinct_product_ids_from_subscriptions() -> list[int]:
    """Возвращает список уникальных артикулов товаров из таблицы подписок."""
    async with AsyncSessionLocal() as session:
        async with session.begin():
            query = select(NotificationSubscription.wb_product_id).distinct()
            result = await session.execute(query)
            product_ids = result.scalars().all()
            return product_ids


async def get_user_ids_subscribed_to_product(product_id: int) -> list[int]:
    """Возвращает список telegram id пользователей, подписанных на товар."""
    async with AsyncSessionLocal() as session:
        async with session.begin():
            query = (
                select(NotificationSubscription.tg_user_id)
                .where(NotificationSubscription.wb_product_id == product_id)
            )
            result = await session.execute(query)
            user_ids = result.scalars().all()
            return user_ids


async def create_wb_product_card(**kwargs) -> None:
    """Создаёт новую запись в таблице карточек товаров."""
    async with AsyncSessionLocal() as session:
        async with session.begin():
            wb_product_card = WBProductCard(**kwargs)
            session.add(wb_product_card)
            await session.commit()


async def get_wb_product_cards_for_user(
    tg_user_id: int
) -> list[PydanticProductCard]:
    """Возвращает список карточек товаров для пользователя."""
    async with AsyncSessionLocal() as session:
        async with session.begin():
            query = select(WBProductCard, WBProduct.name).join(WBProduct).join(
                NotificationSubscription
            ).where(
                NotificationSubscription.tg_user_id == tg_user_id
            ).where(
                WBProductCard.created_at >= NotificationSubscription.created_at
            ).order_by(
                WBProductCard.created_at.desc()
            ).limit(5)
            result = await session.execute(query)
            db_product_cards = result.all()
            pydantic_cards = [
                PydanticProductCard(
                    name=name,
                    id=card.wb_product_id,
                    priceU=card.unit_price,
                    salePriceU=card.sale_price,
                    rating=card.rating,
                    stock=card.stock,
                    created_at=card.created_at
                ) for card, name in db_product_cards
            ]
            return pydantic_cards
