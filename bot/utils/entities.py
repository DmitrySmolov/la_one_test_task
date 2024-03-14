from datetime import datetime

from pydantic import BaseModel


class PydanticProductCard(BaseModel):
    """Модель для карточки товара."""
    name: str | None = None
    id: int | None = None
    priceU: int | None = None
    salePriceU: int | None = None
    rating: int | None = None
    stock: int | None = None
    created_at: datetime | None = None

    @staticmethod
    def _to_user_repr(price: int) -> str:
        """Возвращает цену в удобном для пользователя формате."""
        return '{:.2f}'.format(price / 100)

    def for_user_model_dump(self, with_dt: bool = False) -> dict[str]:
        """Возвращает данные для отображения пользователю."""
        u_price = self._to_user_repr(
            self.priceU
        ) if self.priceU else 'нет данных'
        s_price = self._to_user_repr(
            self.salePriceU
        ) if self.salePriceU else 'нет данных'
        price = f'{s_price} руб. (базовая {u_price} руб.)'
        result = {
            'Название': self.name if self.name else 'нет данных',
            'Артикул': self.id if self.id else ('нет данных'),
            'Цена': price,
            'Рейтинг': self.rating if self.rating else 'нет данных',
            'Количество товара': self.stock if self.stock else 'нет данных'
        }
        if with_dt:
            result['Дата записи'] = self.created_at
        return result

    def for_db_product_model_dump(self) -> dict[str]:
        """Возвращает данные для сохранения товара в бд."""
        return {
            'id': self.id,
            'name': self.name
        }

    def for_db_card_model_dump(self) -> dict[str]:
        """Возвращает данные для сохранения карточки в бд."""
        return {
            'wb_product_id': self.id,
            'unit_price': self.priceU,
            'sale_price': self.salePriceU,
            'rating': self.rating,
            'stock': self.stock
        }
