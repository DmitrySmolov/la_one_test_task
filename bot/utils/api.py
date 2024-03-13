from aiohttp import ClientSession

from bot.utils.entities import WBProductCard
from config import config

WB_API_URL = config.wb_api_url.get_secret_value()


async def get_product_card_from_api(product_id: int) -> WBProductCard | None:
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
            model_data = {key: None for key in WBProductCard.model_fields}
            for key in model_data:
                model_data[key] = product_card_data.get(key, None)
            sizes = product_card_data.get('sizes', [])
            if not sizes:
                model_data['stock'] = None
            else:
                all_stocks = []
                for size in sizes:
                    warehouses = size.get('stocks', [])
                    if not warehouses:
                        continue
                    for warehouse in warehouses:
                        all_stocks.append(warehouse.get('qty', 0))
                if len(all_stocks) == 0:
                    model_data['stock'] = None
                else:
                    model_data['stock'] = sum(all_stocks)
            return WBProductCard(**model_data)
