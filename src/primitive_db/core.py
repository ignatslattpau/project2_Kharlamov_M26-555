import json
from copy import deepcopy

from primitive_db.decorators import (
    confirm_action,
    create_cacher,
    handle_db_errors,
    log_time,
)
from primitive_db.utils import load_table_data

ALLOWED_TYPES = {"int", "str", "bool"}

PYTHON_TYPES = {
    "int": int,
    "str": str,
    "bool": bool,
}

cache_result = create_cacher()


@handle_db_errors
def create_table(metadata, table_name, columns):
    if not table_name.isidentifier():
        raise ValueError(f"Некорректное имя таблицы: {table_name}")

    if table_name in metadata:
        raise ValueError(f'Таблица "{table_name}" уже существует.')

    if not columns:
        raise ValueError("Укажите хотя бы один столбец.")

    new_columns = []
    column_names = set()

    for column in columns:
        parts = column.split(":")

        if len(parts) != 2:
            raise ValueError(f"Некорректное значение: {column}")

        name, data_type = parts

        if not name.isidentifier() or data_type not in ALLOWED_TYPES:
            raise ValueError(f"Некорректное значение: {column}")

        if name in column_names:
            raise ValueError(f"Столбец {name} указан несколько раз.")

        if name == "ID" and data_type != "int":
            raise ValueError("ID должен иметь тип int.")

        column_names.add(name)
        new_columns.append(column)

    if "ID" not in column_names:
        new_columns.insert(0, "ID:int")
    else:
        new_columns.remove("ID:int")
        new_columns.insert(0, "ID:int")

    new_metadata = metadata.copy()
    new_metadata[table_name] = new_columns

    print(
        f'Таблица "{table_name}" успешно создана '
        f'со столбцами: {", ".join(new_columns)}'
    )

    return new_metadata


@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata, table_name):
    if table_name not in metadata:
        raise ValueError(f'Таблица "{table_name}" не существует.')

    new_metadata = metadata.copy()
    del new_metadata[table_name]

    print(f'Таблица "{table_name}" успешно удалена.')

    return new_metadata


@handle_db_errors
@log_time
def insert(metadata, table_name, values):
    if table_name not in metadata:
        raise ValueError(f'Таблица "{table_name}" не существует.')

    columns = metadata[table_name]

    user_columns = [
        col for col in columns
        if col.split(":")[0] != "ID"
    ]

    if len(values) != len(user_columns):
        raise ValueError(
            f"Ожидалось {len(user_columns)} значений, "
            f"получено {len(values)}."
        )

    record = {}

    for column, value in zip(user_columns, values):
        name, data_type = column.split(":")

        expected_type = PYTHON_TYPES[data_type]

        if type(value) is not expected_type:
            raise ValueError(
                f"Некорректное значение: {value!r}. "
                f"Столбец {name} ожидает тип {data_type}."
            )

        record[name] = value

    table_data = load_table_data(table_name)

    new_id = max(
        (row["ID"] for row in table_data),
        default=0,
    ) + 1

    record = {"ID": new_id, **record}
    table_data.append(record)

    print(
        f'Запись с ID={new_id} успешно добавлена '
        f'в таблицу "{table_name}".'
    )

    return table_data


@handle_db_errors
@log_time
def select(table_data, where_clause=None):
    key = json.dumps(
        [table_data, where_clause],
        ensure_ascii=False,
        sort_keys=True,
    )

    def get_result():
        if where_clause is None:
            return deepcopy(table_data)

        return [
            row.copy()
            for row in table_data
            if all(
                row.get(column) == value
                for column, value in where_clause.items()
            )
        ]

    result = cache_result(key, get_result)

    return deepcopy(result)


@handle_db_errors
def update(table_data, set_clause, where_clause):
    updated_data = []
    updated_ids = []

    for row in table_data:
        new_row = row.copy()

        if all(
            row.get(column) == value
            for column, value in where_clause.items()
        ):
            new_row.update(set_clause)
            updated_ids.append(row["ID"])

        updated_data.append(new_row)

    return updated_data, updated_ids


@handle_db_errors
@confirm_action("удаление записи")
def delete(table_data, where_clause):
    deleted_ids = []
    remaining_data = []

    for row in table_data:
        if all(
            row.get(column) == value
            for column, value in where_clause.items()
        ):
            deleted_ids.append(row["ID"])
        else:
            remaining_data.append(row)

    return remaining_data, deleted_ids
