from pydantic import BaseModel


class WBProductCard(BaseModel):
    """Модель для карточки товара."""
    name: str | None
    id: int | None
    priceU: int | None
    salePriceU: int | None
    rating: int | None
    stock: int | None

    @staticmethod
    def _to_user_repr(price: int) -> str:
        """Возвращает цену в удобном для пользователя формате."""
        return '{:.2f}'.format(price / 100)

    def for_user_model_dump(self) -> dict[str]:
        """Возвращает данные для отображения пользователю."""
        u_price = self._to_user_repr(
            self.priceU
        ) if self.priceU else 'нет данных'
        s_price = self._to_user_repr(
            self.salePriceU
        ) if self.salePriceU else 'нет данных'
        price = f'{s_price} руб. (базовая {u_price} руб.)'
        return {
            'name': self.name if self.name else 'нет данных',
            'id': self.id if self.id else ('нет данных'),
            'price': price,
            'rating': self.rating if self.rating else 'нет данных',
            'stock': self.stock if self.stock else 'нет данных'
        }
