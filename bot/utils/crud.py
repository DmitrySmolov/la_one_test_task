from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.utils.entities import PydanticProductCard
from config import config
from db.models import NotificationSubscription, WBProduct, WBProductCard


async def create_wb_product(session: AsyncSession, **kwargs) -> None:
    """Создаёт новую запись в таблице товаров."""
    wb_product = WBProduct(**kwargs)
    session.add(wb_product)


async def check_wb_product_exists(
        session: AsyncSession, wb_product_id: int
) -> bool:
    """Проверяет, существует ли товар с указанным артикулом."""
    query = select(WBProduct).where(WBProduct.id == wb_product_id)
    result = await session.execute(query)
    product = result.scalar()
    return bool(product)


async def create_notification_subscription(
    session: AsyncSession, tg_user_id: int, wb_product_id: int
) -> None:
    """Создаёт новую запись в таблице подписок."""
    subscription = NotificationSubscription(
        tg_user_id=tg_user_id, wb_product_id=wb_product_id
    )
    session.add(subscription)


async def delete_notification_subscription(
    session: AsyncSession, tg_user_id: int, wb_product_id: int
) -> None:
    """Удаляет запись из таблицы подписок."""
    subscription = await get_notification_subscription(
        session, tg_user_id, wb_product_id
    )
    await session.delete(subscription)


async def delete_all_subscriptions_for_user(
        session: AsyncSession, tg_user_id: int
) -> None:
    """Удаляет все подписки пользователя."""
    query = (
        delete(NotificationSubscription).where(
            NotificationSubscription.tg_user_id == tg_user_id
        )
    )
    await session.execute(query)


async def get_notification_subscription(
    session: AsyncSession, tg_user_id: int, wb_product_id: int
) -> NotificationSubscription:
    """Возвращает запись из таблицы подписок."""
    query = (
        select(NotificationSubscription)
        .where(
            NotificationSubscription.tg_user_id == tg_user_id,
            NotificationSubscription.wb_product_id == wb_product_id,
        )
    )
    result = await session.execute(query)
    subscription = result.scalar()
    return subscription


async def get_product_ids_subscribed_by_user(
    session: AsyncSession, tg_user_id: int
) -> list[int]:
    """
    Возвращает список артикулов товаров, на которые подписан пользователь.
    """
    query = select(NotificationSubscription.wb_product_id).where(
        NotificationSubscription.tg_user_id == tg_user_id
    )
    result = await session.execute(query)
    product_ids = result.scalars().all()
    return product_ids


async def subscribe_user_to_product(
    session: AsyncSession, tg_user_id: int, wb_product: PydanticProductCard
) -> None:
    """Подписывает пользователя на товар."""
    wb_product_id = wb_product.id
    if not await check_wb_product_exists(session, wb_product_id):
        await create_wb_product(
            session, **wb_product.for_db_product_model_dump()
        )
    if await get_notification_subscription(
        session, tg_user_id, wb_product_id
    ):
        raise ValueError('Подписка уже существует.')
    await create_notification_subscription(session, tg_user_id, wb_product_id)


async def get_distinct_product_ids_from_subscriptions(
    session: AsyncSession
) -> list[int]:
    """Возвращает список уникальных артикулов товаров из таблицы подписок."""
    query = select(NotificationSubscription.wb_product_id).distinct()
    result = await session.execute(query)
    product_ids = result.scalars().all()
    return product_ids


async def get_user_ids_subscribed_to_product(
    session: AsyncSession, product_id: int
) -> list[int]:
    """Возвращает список telegram id пользователей, подписанных на товар."""
    query = (
        select(NotificationSubscription.tg_user_id)
        .where(NotificationSubscription.wb_product_id == product_id)
    )
    result = await session.execute(query)
    user_ids = result.scalars().all()
    return user_ids


async def create_wb_product_card(session: AsyncSession, **kwargs) -> None:
    """Создаёт новую запись в таблице карточек товаров."""
    wb_product_card = WBProductCard(**kwargs)
    session.add(wb_product_card)


async def get_wb_product_cards_for_user(
    session: AsyncSession, tg_user_id: int
) -> list[PydanticProductCard]:
    """Возвращает список карточек товаров для пользователя."""
    query = select(WBProductCard, WBProduct.name).join(WBProduct).join(
        NotificationSubscription
    ).where(
        NotificationSubscription.tg_user_id == tg_user_id
    ).where(
        WBProductCard.created_at >= NotificationSubscription.created_at
    ).order_by(
        WBProductCard.created_at.desc()
    ).limit(config.product_cards_limit)
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
