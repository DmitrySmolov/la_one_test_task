from bot.utils.entities import PydanticProductCard


def generate_product_info_from_card(
        card: PydanticProductCard, with_dt: bool = False
) -> str:
    """
    Генерирует текстовое представление карточки товара для отправки
    сообщения ботом.
    """
    data = card.for_user_model_dump(with_dt=with_dt)
    text = '\n'.join(
        (f'{key}: {value}' for key, value in data.items())
    )
    return text
