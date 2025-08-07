import json
from unittest.mock import Mock, patch

import pandas
import pytest

from src.services import get_transactions_to_persons, investment_bank


@patch("pandas.read_excel")
def test_get_transactions_to_persons(
    mock_get: Mock, transactions_df: pandas.DataFrame, transactions_df_persons: pandas.DataFrame
) -> None:
    mock_get.return_value = transactions_df_persons
    assert get_transactions_to_persons() == json.dumps(
        [
            {
                "Дата операции": "31.12.2021 00:12:53",
                "Дата платежа": "31.12.2021",
                "Номер карты": "1",
                "Статус": "OK",
                "Сумма операции": -800.0,
                "Валюта операции": "RUB",
                "Сумма платежа": -800.0,
                "Валюта платежа": "RUB",
                "Кэшбэк": "1",
                "Категория": "Переводы",
                "MCC": "1",
                "Описание": "Константин Л.",
                "Бонусы (включая кэшбэк)": 0,
                "Округление на инвесткопилку": 0,
                "Сумма операции с округлением": 800.0,
            },
            {
                "Дата операции": "30.12.2021 22:22:03",
                "Дата платежа": "31.12.2021",
                "Номер карты": "1",
                "Статус": "OK",
                "Сумма операции": -20000.0,
                "Валюта операции": "RUB",
                "Сумма платежа": -20000.0,
                "Валюта платежа": "RUB",
                "Кэшбэк": "1",
                "Категория": "Переводы",
                "MCC": "1",
                "Описание": "Константин Л.",
                "Бонусы (включая кэшбэк)": 0,
                "Округление на инвесткопилку": 0,
                "Сумма операции с округлением": 20000.0,
            },
        ],
        indent=4,
        ensure_ascii=False,
    )

    mock_get.return_value = transactions_df
    assert get_transactions_to_persons() == json.dumps([])


@pytest.mark.parametrize(
    "month, limit, expected",
    [
        ("2021-04", 50, {"amount_saved": 0}),
        ("2021-12", 50, {"amount_saved": 0}),
        ("2021-12", 100, {"amount_saved": 100.00}),
    ],
)
def test_investment_bank(month: str, transactions_investment_list: list, limit: int, expected: dict) -> None:
    assert investment_bank(month, transactions_investment_list, limit) == json.dumps(expected)
    assert investment_bank("2021-12", [], 50) == json.dumps({"amount_saved": 0})
