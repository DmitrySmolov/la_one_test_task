from aiohttp import ClientSession

from bot.utils.entities import PydanticProductCard
from config import config

WB_API_URL = config.wb_api_url.get_secret_value()


async def get_product_card_from_api(
    product_id: int
) -> PydanticProductCard | None:
    """
    Получает данные о товаре из API.
    """
    async with ClientSession() as session:
        async with session.get(WB_API_URL.format(
            product_id=product_id)
        ) as response:
            data = await response.json()
            try:
                product_card_data = data['data']['products'][0]
            except (KeyError, IndexError):
                return None
            pydantic_card = PydanticProductCard()
            for field in pydantic_card.model_fields:
                setattr(
                    pydantic_card, field, product_card_data.get(field, None)
                )
            sizes = product_card_data.get('sizes', [])
            if sizes:
                all_stocks = []
                for size in sizes:
                    warehouses = size.get('stocks', [])
                    if not warehouses:
                        continue
                    for warehouse in warehouses:
                        all_stocks.append(warehouse.get('qty', 0))
                if len(all_stocks) > 0:
                    pydantic_card.stock = sum(all_stocks)
            return pydantic_card
