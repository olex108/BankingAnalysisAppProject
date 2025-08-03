import datetime
import json
from typing import Optional

import pandas as pd
from dateutil.relativedelta import relativedelta


def spending_by_weekday(transactions: pd.DataFrame, date: Optional[str] = None) -> str:
    """
    Функция принимает на вход: дата фрейм с транзакциями, опциональную дату.
    Если дата не передана, то берется текущая дата.

    Функция возвращает средние траты в каждый из дней недели за последние три месяца (от переданной даты).

    :param transactions: Дата фрейм с транзакциями
    :param date: Опциональная дата в формате YYYY-MM-DD
    :return response: json ответ в форме
        {
                "Sunday": 0,
                "Monday": 0,
                "Tuesday": 0,
                "Wednesday": 0,
                "Thursday": 0,
                "Friday": 0,
                "Saturday": 0
        }
    """

    # Проверка, если дата фрейм пустой возвращаем ответ
    if len(transactions) == 0:
        return json.dumps(
            {"Sunday": 0, "Monday": 0, "Tuesday": 0, "Wednesday": 0, "Thursday": 0, "Friday": 0, "Saturday": 0}
        )
    # Определяем трех месячный интервал от заданной даты
    if date is None:
        stop_dt = datetime.datetime.now()
    else:
        stop_dt = datetime.datetime.strptime(date, "%Y-%m-%d")
    start_dt = stop_dt - relativedelta(months=3)

    # Фильтрация по заданному периоду
    transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"], dayfirst=True)
    transactions_df_for_period = transactions[
        (transactions["Дата операции"] >= start_dt)
        & (transactions["Дата операции"] <= stop_dt)
        & (transactions["Статус"] == "OK")
    ]

    # Меняем данные даты операции на день недели
    transactions_df_for_period["Дата операции"] = transactions_df_for_period["Дата операции"].dt.weekday

    # Заполняем словарь трат по дням недели
    dict_of_days_nums = {
        "Sunday": 6,
        "Monday": 0,
        "Tuesday": 1,
        "Wednesday": 2,
        "Thursday": 3,
        "Friday": 4,
        "Saturday": 5,
    }
    response = {}

    # Цикл проверки дата фрейм фильтруется по дню недели и записывает соответствующие данные трат
    for day, num_day in dict_of_days_nums.items():
        transactions_df_per_weekday = transactions_df_for_period[
            (transactions_df_for_period["Дата операции"]) == num_day
        ]
        try:
            response[day] = round(
                abs(float(transactions_df_per_weekday["Сумма операции"].sum()))
                / float(transactions_df_per_weekday["Сумма операции"].count()),
                2,
            )
        except ZeroDivisionError:
            response[day] = 0

    return json.dumps(response)
