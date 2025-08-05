import json
import logging
import os
import re
from datetime import datetime
from typing import Any

from src.utils import get_transactions_list

logger = logging.getLogger("services")
logger.setLevel(logging.DEBUG)

path_to_file = os.path.join(os.path.abspath(__file__), os.pardir, os.pardir, "logs", "services.log")
file_handler = logging.FileHandler(path_to_file, mode="w", encoding="'utf-8")
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def get_transactions_to_persons() -> str:
    """
        $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
        $Сервис "Поиск переводов физическим лицам"$
        $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

    Функция возвращает JSON со всеми транзакциями, которые относятся к переводам физлицам.
    Категория такой транзакции — Переводы, а в описании есть имя и первая буква фамилии с точкой.

    :returns transactions: Список отсортированных транзакций в которых указано Имя и фамилия в описании

        Например:
        Валерий А.
        Сергей З.
        Артем П.
    """

    logger.info(f"Вызов сервиса 'Поиск переводов физическим лицам' {get_transactions_to_persons.__name__}")

    # Извлекаем данные из файла
    path_to_file = os.path.join(os.path.abspath(__file__), os.pardir, os.pardir, "data", "operations.xlsx")
    data_list = get_transactions_list(path_to_file)

    pattern = re.compile(r"\b[А-ЯЁ][а-яе]+\b\s\b[А-ЯЁ]{1}\b\.")

    # Фильтрация по заданному паттерну
    transactions_list = []
    for transaction in data_list:
        if transaction["Категория"] == "Переводы":
            match = re.search(pattern, transaction["Описание"], flags=0)
            if match:
                transactions_list.append(transaction)

    logger.info("Cервис возвращает результат")
    return json.dumps(
        transactions_list,
        indent=4,
        ensure_ascii=False,
    )


def investment_bank(month: str, transactions: list[dict[str, Any]], limit: int) -> str:
    ######################
    #         /\         #
    #    /\  /  \  /\    #
    #   /  \/    \/  \   #
    #  | o |  O  | o |   #
    #  |ИНВЕСТКОПИЛКА|   #
    ######################
    """
    Сервис позволяет копить через округление ваших трат.
    Можно задать комфортный порог округления: 10, 50 или 100 ₽. Траты будут округляться,
    и разница между фактической суммой трат по карте и суммой округления будет попадать на счет «Инвесткопилки».

    Пример
    Вы настроили шаг округления 50 ₽. Покупка на 1712 ₽ автоматически округлится до 1750 ₽,
    и 38 ₽ попадут в «Инвесткопилку».
    Чем активнее расплачиваетесь картой, тем быстрее копятся деньги в копилке.

    Функция принимает на вход три аргумента.
    Возвращает сумму, которую удалось бы отложить в «Инвесткопилку»

    :param month: Месяц, для которого рассчитывается отложенная сумма (строка в формате 'YYYY-MM').
    :param transactions: Список словарей, содержащий информацию о транзакциях, в которых содержатся следующие поля:
        Дата операции — дата, когда произошла транзакция (строка в формате 'YYYY-MM-DD').
        Сумма операции — сумма транзакции в оригинальной валюте (число).
    :param limit: Предел, до которого нужно округлять суммы операций (целое число).
    :return savings_amount: Сумма, которую удалось бы отложить в «Инвесткопилку» в формате
        {"amount_saved": float}
    """

    logger.info(f"Вызов сервиса 'Инвесткопилка' {investment_bank.__name__}")

    # Проверка если транзакции отсутствуют ответ
    if len(transactions) == 0:
        logger.warning("Данные в файле за указанный период отсутствуют")
        return json.dumps({"amount_saved": 0})

    month_dt = datetime.strptime(month, "%Y-%m")
    savings_amount = 0
    total_spends = 0

    for transaction in transactions:
        # Проверка входит ли транзакции в заданный месяц
        if (
            datetime.strptime(transaction["Дата операции"], "%Y-%m-%d").year == month_dt.year
            and datetime.strptime(transaction["Дата операции"], "%Y-%m-%d").month == month_dt.month
        ):
            savings_amount += (
                limit - (abs(transaction["Сумма операции"]) % limit)
                if abs(transaction["Сумма операции"]) % limit != 0
                else 0
            )
            total_spends += transaction["Сумма операции"]

    logger.info("Cервис возвращает результат")
    return json.dumps({"amount_saved": round(savings_amount, 2)})
