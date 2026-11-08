import shlex

import prompt

from primitive_db.core import create_table, drop_table
from primitive_db.utils import load_metadata, save_metadata


METADATA_FILE = "db_meta.json"


def print_help():
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print(
        "<command> create_table <имя_таблицы> "
        "<столбец1:тип> <столбец2:тип> .. - создать таблицу"
    )
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация")
    print()


def run():
    print_help()

    while True:
        metadata = load_metadata(METADATA_FILE)

        try:
            user_input = prompt.string(">>>Введите команду: ")
            args = shlex.split(user_input)
        except ValueError:
            print("Ошибка: Некорректный формат команды.")
            continue
        except (KeyboardInterrupt, EOFError):
            print("\nВыход из программы.")
            break

        if not args:
            continue

        command = args[0]
        arguments = args[1:]

        if command == "exit":
            if arguments:
                print(f"Некорректное значение: {arguments[0]}. Попробуйте снова.")
                continue
            break

        elif command == "help":
            if arguments:
                print(f"Некорректное значение: {arguments[0]}. Попробуйте снова.")
                continue
            print_help()

        elif command == "list_tables":
            if arguments:
                print(f"Некорректное значение: {arguments[0]}. Попробуйте снова.")
                continue

            if not metadata:
                print("Таблиц пока нет.")
            else:
                for table_name in metadata:
                    print(f"- {table_name}")

        elif command == "create_table":
            if len(arguments) < 2:
                print(
                    "Ошибка: Укажите имя таблицы "
                    "и хотя бы один столбец."
                )
                continue

            table_name = arguments[0]
            columns = arguments[1:]

            old_metadata = metadata.copy()

            metadata = create_table(
                metadata, table_name, columns
            )

            if metadata != old_metadata:
                save_metadata(METADATA_FILE, metadata)

        elif command == "drop_table":
            if len(arguments) != 1:
                print(
                    "Ошибка: Команда drop_table "
                    "принимает одно имя таблицы."
                )
                continue

            table_name = arguments[0]

            old_metadata = metadata.copy()

            metadata = drop_table(metadata, table_name)

            if metadata != old_metadata:
                save_metadata(METADATA_FILE, metadata)

        else:
            print(f"Функции {command} нет. Попробуйте снова.")