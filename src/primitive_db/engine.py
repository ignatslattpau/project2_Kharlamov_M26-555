import re
import shlex

import prompt
from prettytable import PrettyTable

from primitive_db.constants import META_FILE, PYTHON_TYPES
from primitive_db.core import (
    create_table,
    delete,
    drop_table,
    insert,
    select,
    update,
)
from primitive_db.parser import parse_condition, parse_values
from primitive_db.utils import (
    delete_table_data,
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)


def print_help():
    """Выводит справочную информацию о командах базы данных."""
    print("\n***Операции с данными***")
    print("\nФункции:")

    commands = [
        "create_table <имя> <столбец:тип> ... - создать таблицу",
        "list_tables - показать список таблиц",
        "drop_table <имя> - удалить таблицу",
        "insert into <имя_таблицы> values (<значение1>, <значение2>, ...) - создать запись.", # noqa: E501
        "select from <имя_таблицы> where <столбец> = <значение> - прочитать записи по условию.", # noqa: E501
        "select from <имя_таблицы> - прочитать все записи.",
        "update <имя_таблицы> set <столбец1> = <новое_значение1> where <столбец_условия> = <значение_условия> - обновить запись.", # noqa: E501
        "delete from <имя_таблицы> where <столбец> = <значение> - удалить запись.",
        "info <имя_таблицы> - вывести информацию о таблице.",
        "exit - выход из программы",
        "help - справочная информация",
    ]

    for command in commands:
        print(f"<command> {command}")

    print()


def check_table(metadata, table_name):
    """Проверяет существование таблицы в метаданных."""
    if table_name not in metadata:
        raise ValueError(
            f'Ошибка: Таблица "{table_name}" не существует.'
        )


def get_schema(metadata, table_name):
    """Возвращает схему таблицы в виде словаря столбцов и типов."""
    check_table(metadata, table_name)

    return dict(
        column.split(":") for column in metadata[table_name]
    )


def validate_condition(metadata, table_name, condition):
    """Проверяет существование столбца и тип значения в условии."""
    schema = get_schema(metadata, table_name)

    for column, value in condition.items():
        if column not in schema:
            raise ValueError(
                f'Ошибка: Столбец "{column}" не существует.'
            )

        expected_type = PYTHON_TYPES[schema[column]]

        if type(value) is not expected_type:
            raise ValueError(
                f"Некорректное значение: {value!r}. "
                f"Для столбца {column} требуется {schema[column]}."
            )


def print_table(metadata, table_name, rows):
    """Выводит записи таблицы в консоль с помощью PrettyTable."""
    columns = [
        column.split(":")[0]
        for column in metadata[table_name]
    ]

    table = PrettyTable()
    table.field_names = columns

    for row in rows:
        table.add_row([row[column] for column in columns])

    print(table)


def run():
    """Запускает основной цикл обработки пользовательских команд."""
    print_help()

    while True:
        metadata = load_metadata(META_FILE)

        try:
            user_input = prompt.string(">>>Введите команду: ").strip()

            if not user_input:
                continue

            command = user_input.split()[0].lower()

            if command == "exit":
                if user_input.lower() != "exit":
                    raise ValueError(
                        "Ошибка: Команда exit не принимает аргументы."
                    )
                print("Выход из программы.")
                break

            elif command == "help":
                if user_input.lower() != "help":
                    raise ValueError(
                        "Ошибка: Команда help не принимает аргументы."
                    )
                print_help()



            elif command == "create_table":

                args = shlex.split(user_input)

                if len(args) < 3:
                    raise ValueError(
                        "Ошибка: Укажите имя таблицы "
                        "и хотя бы один столбец."
                    )

                table_name = args[1]
                columns = args[2:]

                result = create_table(metadata, table_name, columns)

                if result is not None:
                    save_metadata(META_FILE, result)

            elif command == "list_tables":
                if user_input.lower() != "list_tables":
                    raise ValueError(
                        "Ошибка: list_tables не принимает аргументы."
                    )

                if not metadata:
                    print("Таблиц пока нет.")
                else:
                    for table_name in metadata:
                        print(f"- {table_name}")

            elif command == "drop_table":
                args = shlex.split(user_input)

                if len(args) != 2:
                    raise ValueError(
                        "Ошибка: Укажите одно имя таблицы."
                    )

                table_name = args[1]

                result = drop_table(metadata, table_name)

                if result is not None:
                    save_metadata(META_FILE, result)
                    delete_table_data(table_name)

            elif command == "insert":
                match = re.fullmatch(
                    r"insert\s+into\s+(\w+)\s+"
                    r"values\s*\((.*)\)\s*",
                    user_input,
                    re.IGNORECASE,
                )

                if not match:
                    raise ValueError("Ошибка: Некорректный INSERT.")

                table_name = match.group(1)
                values = parse_values(match.group(2))
                result = insert(metadata, table_name, values)

                if result is not None:
                    save_table_data(table_name, result)


            elif command == "select":
                match = re.fullmatch(
                    r"select\s+from\s+(\w+)"
                    r"(?:\s+where\s+(.+))?\s*",
                    user_input,
                    re.IGNORECASE,
                )

                if not match:
                    raise ValueError("Ошибка: Некорректный SELECT.")

                table_name = match.group(1)
                check_table(metadata, table_name)
                table_data = load_table_data(table_name)

                if match.group(2):
                    where_clause = parse_condition(match.group(2))
                    validate_condition(
                        metadata, table_name, where_clause
                    )
                    result = select(table_data, where_clause)

                else:
                    result = select(table_data)
                if result is not None:
                    print_table(metadata, table_name, result)


            elif command == "update":
                match = re.fullmatch(
                    r"update\s+(\w+)\s+set\s+(.+?)"
                    r"\s+where\s+(.+)",
                    user_input,
                    re.IGNORECASE,
                )

                if not match:
                    raise ValueError("Ошибка: Некорректный UPDATE.")

                table_name = match.group(1)
                set_clause = parse_condition(match.group(2))
                where_clause = parse_condition(match.group(3))
                validate_condition(metadata, table_name, set_clause)
                validate_condition(metadata, table_name, where_clause)

                if "ID" in set_clause:
                    raise ValueError(
                        "Ошибка: Нельзя изменять первичный ключ ID."
                    )

                table_data = load_table_data(table_name)
                result = update(table_data, set_clause, where_clause)
                if result is not None:
                    new_data, updated_ids = result
                    if updated_ids:
                        save_table_data(table_name, new_data)
                        for record_id in updated_ids:
                            print(
                                f'Запись с ID={record_id} в таблице '
                                f'"{table_name}" успешно обновлена.'
                            )

                    else:
                        print("Записи по условию не найдены.")


            elif command == "delete":
                match = re.fullmatch(
                    r"delete\s+from\s+(\w+)"
                    r"\s+where\s+(.+)",
                    user_input,
                    re.IGNORECASE,
                )

                if not match:
                    raise ValueError("Ошибка: Некорректный DELETE.")

                table_name = match.group(1)
                where_clause = parse_condition(match.group(2))
                validate_condition(metadata, table_name, where_clause)
                table_data = load_table_data(table_name)
                result = delete(table_data, where_clause)

                if result is not None:
                    new_data, deleted_ids = result
                    if deleted_ids:
                        save_table_data(table_name, new_data)

                        for record_id in deleted_ids:
                            print(
                                f"Запись с ID={record_id} успешно "
                                f'удалена из таблицы "{table_name}".'
                            )
                    else:
                        print("Записи по условию не найдены.")


            elif command == "info":
                args = shlex.split(user_input)

                if len(args) != 2:
                    raise ValueError(
                        "Ошибка: Укажите одно имя таблицы."
                    )

                table_name = args[1]
                check_table(metadata, table_name)

                table_data = load_table_data(table_name)

                print(f"Таблица: {table_name}")
                print(
                    f"Столбцы: {', '.join(metadata[table_name])}"
                )
                print(f"Количество записей: {len(table_data)}")

            else:
                print(
                    f"Функции {command} нет. Попробуйте снова."
                )

        except ValueError as error:
            print(error)

        except (KeyboardInterrupt, EOFError):
            print("\nВыход из программы.")
            break
