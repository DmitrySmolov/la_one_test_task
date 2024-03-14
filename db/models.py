from datetime import datetime

from sqlalchemy import (
    DateTime, ForeignKey, SmallInteger, UniqueConstraint
)
from sqlalchemy.orm import (
    declarative_base, Mapped, mapped_column
)

Base = declarative_base()


class WBProduct(Base):
    """
    Модель товара с Wildberries. Значения id и name из API Wildberries.
    """
    __tablename__ = 'wb_products'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)

    def __repr__(self) -> str:
        return f'WBProduct(id={self.id}, name={self.name})'


class WBProductCard(Base):
    """
    Модель карточки товара с Wildberries.
    """
    __tablename__ = 'wb_product_cards'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    wb_product_id: Mapped[int] = mapped_column(
        ForeignKey('wb_products.id'), nullable=False, index=True
    )
    unit_price: Mapped[int] = mapped_column(nullable=False)
    sale_price: Mapped[int] = mapped_column(nullable=False)
    rating: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    stock: Mapped[int] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now, index=True
    )

    def __repr__(self) -> str:
        return (
            f'WBProductCard(wb_product_id={self.wb_product_id}, '
            f'created_at={self.created_at})'
        )


class NotificationSubscription(Base):
    """
    Модель подписки телеграм-пользователя уведомления с карточками товара.

    """
    __tablename__ = 'notification_subscriptions'
    __table_args__ = (
        UniqueConstraint(
            'tg_user_id', 'wb_product_id', name='unique_user_product'
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_user_id: Mapped[int] = mapped_column(nullable=False, index=True)
    wb_product_id: Mapped[int] = mapped_column(
        ForeignKey('wb_products.id'), nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now, index=True
    )

    def __repr__(self) -> str:
        return (
            f'NotificationSubscription(tg_user_id={self.tg_user_id}, '
            f'wb_product_id={self.wb_product_id})'
        )
