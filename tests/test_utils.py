import unittest
from unittest.mock import Mock, patch

import pandas
from freezegun import freeze_time

from src.utils import (get_cards_spends_list, get_currency_rates, get_greeting_massage, get_stock_prices,
                       get_top_transaction_list, get_transactions_list_for_period, get_user_settings)


@freeze_time("2025-04-01 11:00:00")
def test_get_greeting_massage() -> None:
    assert get_greeting_massage() == "Доброе утро"


@patch("json.load")
def test_get_user_settings(mock_get: Mock) -> None:
    mock_get.return_value = {
        "user_currencies": ["USD", "EUR"],
        "user_stocks": ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"],
    }

    assert get_user_settings() == {
        "user_currencies": ["USD", "EUR"],
        "user_stocks": ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"],
    }


def test_get_user_settings_file_error() -> None:
    with patch("builtins.open") as mock_file:
        mock_file.side_effect = FileNotFoundError
        assert get_user_settings() == {"user_currencies": [], "user_stocks": []}


@patch("pandas.read_excel")
def test_get_transactions_list_for_period(mock_get: Mock, transactions_df: pandas.DataFrame) -> None:

    mock_get.return_value = pandas.DataFrame(transactions_df)

    assert get_transactions_list_for_period(
        "2021-12-02 23:40:34",
        "data/operations.xlsx") == transactions_df.to_dict("records")

    mock_get.return_value = pandas.DataFrame(
        {
            "Дата операции": [],
            "Дата платежа": [],
            "Номер карты": [],
            "Статус": [],
            "Сумма операции": [],
            "Валюта операции": [],
            "Сумма платежа": [],
            "Валюта платежа": [],
            "Кэшбэк": [],
            "Категория": [],
            "MCC": [],
            "Описание": [],
            "Бонусы (включая кэшбэк)": [],
            "Округление на инвесткопилку": [],
            "Сумма операции с округлением": [],
        }
    )

    assert get_transactions_list_for_period("2021-12-02 23:40:34", "data/operations.xlsx") == []


def test_get_cards_spends_list(transactions_df: pandas.DataFrame) -> None:

    assert get_cards_spends_list(transactions_df.to_dict(orient="records")) == [
        {"last_digits": "7197", "total_spent": -398.29, "cashback": 3.98},
    ]

    empty_list: list = []
    assert get_cards_spends_list(empty_list) == []


def test_get_top_transaction_list(transactions_df: pandas.DataFrame) -> None:
    assert get_top_transaction_list(transactions_df.to_dict(orient="records")) == [
        {"date": "01.12.2021", "amount": 199.0, "category": "Дом и ремонт", "description": "Строитель"},
        {"date": "01.12.2021", "amount": 99.22, "category": "Супермаркеты", "description": "Дикси"},
        {"date": "01.12.2021", "amount": 99.0, "category": "Фастфуд", "description": "IP Yakubovskaya M.V."},
        {"date": "02.12.2021", "amount": 1.07, "category": "Каршеринг", "description": "Ситидрайв"},
    ]


def test_get_currency_rates() -> None:
    # Задаем фиктивный ответ от API
    mock_api_response = {"Valute": {"USD": {"Value": 75.0}, "EUR": {"Value": 80.0}}}

    with patch("requests.get") as mock_get:
        # Настраиваем заглушку для requests.get
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_api_response

        # Проверяем, что функция возвращает ожидаемые данные
        expected_result = [
            {"currency": "USD", "rate": 75.0},
            {"currency": "EUR", "rate": 80.0},
        ]
        assert get_currency_rates({"user_currencies": ["USD", "EUR"]}) == expected_result

        # Проверяем, что requests.get был вызван с правильным URL
        mock_get.assert_called_once_with("https://www.cbr-xml-daily.ru/daily_json.js")

    with patch("requests.get") as mock_get:
        # Настраиваем заглушку для requests.get
        mock_get.return_value.status_code = 404
        mock_get.return_value.json.return_value = mock_api_response

        # Проверяем, что функция возвращает ожидаемые данные
        expected_result = []
        assert get_currency_rates({"user_currencies": ["USD", "EUR"]}) == expected_result
        #


class TestStockPrices(unittest.TestCase):
    @patch("requests.get")
    @patch("os.getenv")
    def test_get_stock_prices(self, mock_getenv: Mock, mock_requests_get: Mock) -> None:
        # Настраиваем заглушку для os.getenv
        mock_getenv.return_value = "fake_api_key"

        # Настраиваем заглушку для requests.get
        mock_response = mock_requests_get.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = {"Global Quote": {"05. price": "150.00"}}

        # Вызываем тестируемую функцию
        result = get_stock_prices(
            {
                "user_currencies": ["USD", "EUR"],
                "user_stocks": ["AAPL", "AMZN"],
            }
        )

        # Проверяем результат
        expected_result = [
            {"stock": "AAPL", "price": "150.00"},
            {"stock": "AMZN", "price": "150.00"},
        ]
        self.assertEqual(result, expected_result)
