import json
import logging
import os
from datetime import datetime
from typing import Any

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("utils")
logger.setLevel(logging.DEBUG)

path_to_file = os.path.join(os.path.abspath(__file__), os.pardir, os.pardir, "logs", "utils.log")
file_handler = logging.FileHandler(path_to_file, mode="w", encoding="'utf-8")
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def get_user_settings() -> Any:
    """
    Функция для получения данных настроек пользователя из JSON - файла. "/data/user_settings.json"

    :return user_settings: словарь в формате
        {
          "user_currencies": ["str", "str"],
          "user_stocks": ["str", "str"]
        }
    """

    logger.info(f"Вызов функции {get_user_settings.__name__}")

    path_to_file = os.path.join(os.path.abspath(__file__), os.pardir, os.pardir, "data", "user_settings.json")
    try:
        with open(path_to_file, "r") as jf:
            user_settings = json.load(jf)
    except FileNotFoundError as ex:
        logger.error(f"Файл по заданному пути отсутствует {ex}")
        return {"user_currencies": [], "user_stocks": []}

    logger.info(f"Функция {get_user_settings.__name__} возвращает данные из файла")

    return user_settings


def get_transactions_list(path_to_file: str) -> list:
    """
    Функция для получения списка данных операций пользователя из EXCEL - файла.

    :param path_to_file: Абсолютный путь к файлу
    :return: список транзакций
    """

    logger.info(f"Вызов функции {get_transactions_list.__name__}")
    return pd.read_excel(path_to_file).to_dict(orient="records")


def get_transactions_df(path_to_file: str) -> pd.DataFrame:
    """
    Функция для получения дата фрейма данных операций пользователя из EXCEL - файла.

    :param path_to_file: Абсолютный путь к файлу
    :return: список транзакций
    """

    logger.info(f"Вызов функции {get_transactions_df.__name__}")
    return pd.read_excel(path_to_file)


def get_transactions_list_for_period(date_time_str: str, path_to_file: str) -> list[dict]:
    """
    Функция для получения списка данных за определенный период операций пользователя из EXCEL - файла.
    Принимает на вход дату и путь к файлу.
    Возвращает список с выборкой по периоду с начала месяца до заданной даты

    :param date_time_str: Строка с датой и временем в формате YYYY-MM-DD HH:MM:SS
    :param path_to_file: Абсолютный путь к файлу
    :return transactions_df.to_dict: список транзакций за указанный период
    """

    logger.info(f"Вызов функции {get_transactions_list_for_period.__name__}")

    stop_dt = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S")
    start_dt = datetime(stop_dt.year, stop_dt.month, 1, 0, 0, 0)

    try:
        operations_data = pd.read_excel(path_to_file)
        if len(operations_data) == 0:

            logger.warning("Данные в файле не соответствуют ожидаемому формату")
            return []

        # Фильтрация по заданному периоду
        operations_data["Дата операции"] = pd.to_datetime(operations_data["Дата операции"], dayfirst=True)
        transactions_df = operations_data.loc[
            (operations_data["Дата операции"] >= start_dt)
            & (operations_data["Дата операции"] <= stop_dt)
            & (operations_data["Статус"] == "OK")
        ]

        logger.info("Функция возвращает данные из файла")
        return transactions_df.to_dict("records")

    except FileNotFoundError as ex:

        logger.error(f"Файл по заданному пути отсутствует {ex}")
        return []


def get_greeting_massage() -> str:
    """
    Функция возвращает строку в зависимости от времени суток

    :return greeting_massage: Строка с одной из строк «Доброе утро» / «Добрый день» / «Добрый вечер» / «Доброй ночи»
    """

    logger.info(f"Вызов функции {get_greeting_massage.__name__}")

    if 6 <= datetime.now().hour < 12:
        greeting_massage = "Доброе утро"
    elif 12 <= datetime.now().hour < 18:
        greeting_massage = "Добрый день"
    elif 18 <= datetime.now().hour < 24:
        greeting_massage = "Добрый вечер"
    else:
        greeting_massage = "Доброй ночи"

    logger.info("Функция возвращает результат")
    return greeting_massage


def get_cards_spends_list(transactions_list: list[dict]) -> list[dict]:
    """
    Функция для получения списка трат по каждой карте списка операций.
    Функция принимает дата фрейм, по множеству номеров карт из данных вычисляется сумма расходов и кэшбэк.

    :param transactions_list: Данные в формате дата фрейма
    :return cards_spend_list: Список словарей в формате
        {
            "last_digits": card_number,
            "total_spent": total_card_spend,
            "cashback": card_cashback,
        }
    """

    logger.info(f"Вызов функции {get_cards_spends_list.__name__}")

    if len(transactions_list) == 0:
        logger.warning("Данные в файле отсутствуют")
        return []

    transactions_df = pd.DataFrame(transactions_list)
    # Получаем номера карт
    cards_numbers = set(transactions_df["Номер карты"])

    # Создаем список словарей
    cards_spend_list = []

    for cadr in cards_numbers:

        if isinstance(cadr, str):
            card_number = cadr[-4:]

            # Фильтруем дата фрейм по номеру карты и сумме операции (отрицательное значение - это расходы)
            card_review = transactions_df[
                (transactions_df["Номер карты"] == cadr) & (transactions_df["Сумма операции"] < 0)
            ]

            total_card_spend = round(float(card_review["Сумма операции"].sum()), 2)
            card_cashback = abs(round(total_card_spend / 100, 2))

            cards_spend_list.append(
                {
                    "last_digits": card_number,
                    "total_spent": total_card_spend,
                    "cashback": card_cashback,
                }
            )

    logger.info("Функция возвращает отсортированные данные из файла")
    return cards_spend_list


def get_top_transaction_list(transactions_list: list[dict]) -> list[dict]:
    """
    Функция для получения списка ТОП 5 транзакций по данным списка операций.
    Функция принимает дата фрейм, сортирует список транзакций, выводит первые 5 элементов списка.

    :param transactions_list: Данные в формате дата фрейма
    :return cards_spend_list: Список словарей в формате
           {
               "date": operation["Дата платежа"],
               "amount": operation["Сумма операции с округлением"],
               "category": operation["Категория"],
               "description": operation["Описание"],
           }
    """

    logger.info(f"Вызов функции {get_top_transaction_list.__name__}")

    top_operations_list = sorted(
        transactions_list,
        key=lambda x: int(x["Сумма операции с округлением"]),
        reverse=True,
    )[0:5]

    response_top_transactions_list = []

    for operation in top_operations_list:
        response_top_transactions_list.append(
            {
                "date": operation["Дата платежа"],
                "amount": operation["Сумма операции с округлением"],
                "category": operation["Категория"],
                "description": operation["Описание"],
            }
        )

    logger.info("Функция возвращает отсортированные данные из файла")
    return response_top_transactions_list


def get_currency_rates(user_settings: dict[Any, Any]) -> list:
    """
    Функция для получения данных курсов валют.
    Принимает данные настроек пользователя и возвращает список курсов валют.
    Данные получает из сайта https://www.cbr-xml-daily.ru

    :param user_settings: Словарь с настройками пользователя
    :return request_list: Список словарей в формате
        {
            "currency": currency,
            "rate": data["Valute"][currency]["Value"]
        }
    """

    logger.info(f"Вызов функции {get_currency_rates.__name__}")

    # Получаем список валют из настроек пользователя
    list_of_currencies = user_settings["user_currencies"]

    # Получаем данные по курсам через API запрос
    response = requests.get("https://www.cbr-xml-daily.ru/daily_json.js")
    data = response.json()

    # Создаем список словарей со заданным валютам
    request_list = []

    if response.status_code == 200:
        for currency in list_of_currencies:
            request_list.append({"currency": currency, "rate": data["Valute"][currency]["Value"]})
    else:
        logger.error(f"Сайт не отвечает. Ответ {response.status_code}")

    logger.info("Функция возвращает данные из сайта")
    return request_list


def get_stock_prices(user_settings: dict[Any, Any]) -> list[dict]:
    """
    Функция для получения стоимости акций из S&P500.
    Принимает данные настроек пользователя и возвращает список стоимости акций API ответом с ресурса Alpha Vantage.
    Данные получает url - https://www.alphavantage.co/support/#api-key

    :param user_settings: Словарь с настройками пользователя
    :return request_list: Список словарей в формате
        {
            "stock": stock,
            "price": data["Global Quote"]["05. price"],
        }
    """

    logger.info(f"Вызов функции {get_stock_prices.__name__}")

    # Извлекаем ключ
    api_key = os.getenv("API-key")
    # Получаем список компаний из данных настройками пользователя
    list_of_stocks = user_settings["user_stocks"]
    # ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]

    stock_prices_list = []

    for stock in list_of_stocks:
        # Получаем данные по стоимости через API запрос
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={stock}&apikey={api_key}"
        request = requests.get(url)
        data = request.json()

        if request.status_code == 200:
            stock_prices_list.append(
                {
                    "stock": stock,
                    "price": data["Global Quote"]["05. price"],
                }
            )
        else:
            logger.error(f"Сайт по запросу компании {stock} не отвечает. Ответ {request.status_code}")

    logger.info("Функция возвращает данные")
    return stock_prices_list
