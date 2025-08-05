import json
import logging
import os

from utils import (
    get_cards_spends_list,
    get_currency_rates,
    get_greeting_massage,
    get_stock_prices,
    get_top_transaction_list,
    get_transactions_list_for_period,
    get_user_settings,
)

logger = logging.getLogger("views")
logger.setLevel(logging.DEBUG)

path_to_file = os.path.join(os.path.abspath(__file__), os.pardir, os.pardir, "logs", "views.log")
file_handler = logging.FileHandler(path_to_file, mode="w", encoding="'utf-8")
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def get_main_page_request(date_time_str: str) -> str:
    """
    Функция, принимающую на вход строку с датой и временем
    и возвращающую JSON-ответ со следующими данными

    1. Приветствие в формате: "???", где ??? — «Доброе утро» / «Добрый день» / «Добрый вечер» / «Доброй ночи»
    в зависимости от текущего времени, вызывает функцию get_greeting_massage.
    2. По каждой карте (вызывает функцию get_cards_spends_list):
    - последние 4 цифры карты;
    - общая сумма расходов;
    - кешбэк (1 рубль на каждые 100 рублей).
    3. Топ-5 транзакций по сумме платежа(вызывает функцию в get_top_transaction_list).
    4. Курс валют (вызывает функцию).
    5. Стоимость акций из S&P500 (вызывает функцию get_stock_prices).

    :param date_time_str : Строка с датой и временем в формате YYYY-MM-DD HH:MM:SS
    :return json_resp: JSON - ответ в формате
        {
            "greeting": greeting_massage,
            "cards": cards_spend_list,
            "top_transactions": top_transaction_list,
            "currency_rates": currency_rates,
            "stock_prices": stock_prices_list,
        }
    """

    logger.info(f"Вызов функции {get_main_page_request.__name__}")
    # Получаем приветственное сообщение в зависимости от времени обращения вызовом функции
    greeting_massage = get_greeting_massage()

    # Получаем данные из списка операций пользователя за указанный период
    path_to_operations_file = os.path.join(os.path.abspath(__file__), os.pardir, os.pardir, "data", "operations.xlsx")
    transactions_list = get_transactions_list_for_period(date_time_str, path_to_operations_file)
    # Получаем траты по каждой карте за указанный период
    cards_spend_list = get_cards_spends_list(transactions_list)
    # Получаем список Топ - 5 транзакций за указанный период
    top_transaction_list = get_top_transaction_list(transactions_list)
    # Получаем данные настроек аккаунта пользователя
    user_settings = get_user_settings()
    # Получаем список акций из S&P500
    stock_prices_list = get_stock_prices(user_settings)
    user_settings = get_user_settings()
    # Получаем список курсов валют
    currency_rates = get_currency_rates(user_settings)

    json_resp = json.dumps(
        {
            "greeting": greeting_massage,
            "cards": cards_spend_list,
            "top_transactions": top_transaction_list,
            "currency_rates": currency_rates,
            "stock_prices": stock_prices_list,
        },
        indent=4,
        ensure_ascii=False,
    )

    logger.info(f"Функция {get_main_page_request.__name__} возвращает JSON ответ")
    return json_resp


#
# print(get_json_request(date_time_str="2022-12-05 10:00:00"))
