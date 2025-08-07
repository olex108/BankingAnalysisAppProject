import datetime
import os
import re

from src.reports import spending_by_weekday
from src.services import get_transactions_to_persons, investment_bank
from src.utils import get_transactions_df, get_transactions_list
from src.views import get_main_page_request


def main() -> None:
    """
    Функция main для получения результатов всех реализованных в проекте функциональностей.:

    - Выбор функциональности:

        1.  Страница «Главная»
        2.  Сервис "Поиск переводов физическим лицам"
        3. Сервис "Инвесткопилка"
        4. Отчет "Траты по дням недели"

            1. Страница «Главная»

            - Принимает дату сортировки
            - Проверка правильности формата даты
            - Вызов функции get_main_page_request

            2. Сервис "Поиск переводов физическим лицам"

            - Вызов функции get_transactions_to_persons

            3. Сервис "Инвесткопилка"

            - Принимает дату сортировки
            - Проверка правильности формата даты
            - Принимает список транзакций
            - Преобразовывает список в нужный формат
            - Принимает лимит для функции
            - Проверяет правильность ввода лимита
            - Вызов функции investment_bank

            4. Отчет "Траты по дням недели"

            - Принимает дату сортировки
            - Проверка правильности формата даты
            - Принимает дата фрейм транзакций
            - Вызов функции spending_by_weekday

    """

    path_to_operations_file = os.path.join(os.path.abspath(__file__), os.pardir, os.pardir, "data", "operations.xlsx")

    while True:
        print(
            """
        Получить результат всех реализованных в проекте функциональностей:
        1.  Страница «Главная»
        2.  Сервис "Поиск переводов физическим лицам"
        3. Сервис "Инвесткопилка"
        4. Отчет "Траты по дням недели"
        """
        )
        user_func = input("Введите номер функции:")

        if user_func == "1":
            while True:
                print(
                    """
            Страница «Главная»
            ВВедите строку с датой и временем в формате YYYY-MM-DD HH:MM:SS
                """
                )

                date = input(">>>")
                pattern = re.compile(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}")

                match = re.search(pattern, date)
                if match:
                    print(get_main_page_request(date))
                    break

                else:
                    print("Неверный формат")

        elif user_func == "2":
            print(
                """
            Сервис "Поиск переводов физическим лицам"
            """
            )
            print(get_transactions_to_persons())

        elif user_func == "3":
            while True:
                print(
                    """
            Сервис "Инвесткопилка"
            ВВедите месяц, для которого рассчитывается отложенная сумма (строка в формате 'YYYY-MM').
                """
                )
                date = input(">>>")

                pattern = re.compile(r"\d{4}-\d{2}")

                match = re.search(pattern, date)
                if match:

                    transactions_list = get_transactions_list(path_to_file=path_to_operations_file)
                    # Преобразовываем список словарей в ожидаемый формат
                    transactions_list = [
                        {
                            "Дата операции": datetime.datetime.strptime(
                                x["Дата операции"], "%d.%m.%Y %H:%M:%S"
                            ).strftime("%Y-%m-%d"),
                            "Сумма операции": x["Сумма операции"],
                        }
                        for x in transactions_list
                    ]

                    print(
                        """
            ВВедите предел, до которого нужно округлять суммы операций (целое число).
                    """
                    )
                    limit = input(">>>")
                    if limit.isdigit():

                        print(investment_bank(date, transactions_list, int(limit)))
                        break

                else:
                    print("Неверный формат")

        elif user_func == "4":
            while True:
                print(
                    """
            Отчет "Траты по дням недели"
            ВВедите строку с датой и временем в формате YYYY-MM-DD
                """
                )

                date = input(">>>")
                pattern = re.compile(r"\d{4}-\d{2}-\d{2}")

                match = re.search(pattern, date)
                if match:

                    transactions_df = get_transactions_df(path_to_file=path_to_operations_file)

                    print(spending_by_weekday(transactions_df, date))
                    break
                else:
                    print("Неверный формат")

        else:
            print("Неверный формат")


if __name__ == "__main__":
    main()
