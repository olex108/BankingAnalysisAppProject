import json

import pandas

from src.reports import spending_by_weekday


def test_spending_by_weekday(
    transactions_df_persons: pandas.DataFrame, transactions_empty_df: pandas.DataFrame
) -> None:
    assert spending_by_weekday(transactions_df_persons, "2022-01-31") == json.dumps(
        {
            "Sunday": 0,
            "Monday": 0,
            "Tuesday": 0,
            "Wednesday": 99.57,
            "Thursday": 20000.0,
            "Friday": 800.0,
            "Saturday": 0,
        }
    )
    assert spending_by_weekday(transactions_empty_df, "2021-01-21") == json.dumps(
        {"Sunday": 0, "Monday": 0, "Tuesday": 0, "Wednesday": 0, "Thursday": 0, "Friday": 0, "Saturday": 0}
    )
