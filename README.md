# Тестовое задание для "LaOne"

Данный проект - это асинхронный Telegram-бот c CУБД PostgreSQL.
Бот принимает от пользователя артикулы товаров с торговой площадки Wildberries и составляет соответствующую артикулу карточку товара. Бот может осуществлять отправку карточек пользователям на те товары, на которые они подписаны а также выводить в сообщении 5 последних карточек из подписки.

## Технологии

- Python 3.12
- Aiogram 3.4
- SQLAlchemy 2.0
- APScheduler 3.10

## Структура проекта

```
.
├──alembic/
│    ├── versions/
│    ├── env.py
│    ├── README
│    └── script.py.mako
├──bot/
│    ├── handlers/
│    │   ├── __init__.py
│    │   ├── database_info.py
│    │   ├── get_product_info.py
│    │   └── stop_notifications.py
│    ├── utils/
│    │   ├── __init__.py
│    │   ├── api.py
│    │   ├── crud.py
│    │   ├── entities.py
│    │   ├── jobs.py
│    │   └── text.py
│    ├── __init__.py
│    └── main.py
├──db/
│    ├── __init__.py
│    ├── models.py
│    └── session.py
├── alembic.ini
├── config.py
├── docker-compose.yml
├── Dockerfile
├──entrypoint.sh
└──requirements.txt
```

## Конфигурации

Все ключевые конфигурации приложения выставлены в файле `config.py` в корне репозитория.

## Использование

Проект развёрнут в облачном сервисе (по состоянию на 16.03.2024). Можете попробовать его по адресу @omo4000bot.\\
Доступные кнопки меню:
- /get_product_info: для получения карточки и подписки на карточки
- /stop_notifications: для остановки подписок (выборочно или всех)
- /get_info_from_db: для вывода 5 последних карточек, которые бот отправлял по подписке
