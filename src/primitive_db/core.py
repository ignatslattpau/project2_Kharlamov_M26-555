from primitive_db.utils import delete_table_data, load_table_data

ALLOWED_TYPES = {"int", "str", "bool"}


def create_table(metadata, table_name, columns):
    if not table_name.isidentifier():
        print(f"Некорректное значение: {table_name}. Попробуйте снова.")
        return metadata

    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return metadata

    if not columns:
        print("Ошибка: Укажите хотя бы один столбец.")
        return metadata

    new_columns = []
    column_names = set()

    for column in columns:
        parts = column.split(":")

        if len(parts) != 2:
            print(f"Некорректное значение: {column}. Попробуйте снова.")
            return metadata

        name, data_type = parts

        if not name.isidentifier() or data_type not in ALLOWED_TYPES:
            print(f"Некорректное значение: {column}. Попробуйте снова.")
            return metadata

        if name in column_names:
            print(f"Ошибка: Столбец {name} указан несколько раз.")
            return metadata

        if name == "ID" and data_type != "int":
            print("Некорректное значение: ID должен иметь тип int.")
            return metadata

        column_names.add(name)
        new_columns.append(column)

    if "ID" not in column_names:
        new_columns.insert(0, "ID:int")
    else:
        new_columns.remove("ID:int")
        new_columns.insert(0, "ID:int")

    metadata[table_name] = new_columns

    print(
        f'Таблица "{table_name}" успешно создана '
        f'со столбцами: {", ".join(new_columns)}'
    )

    return metadata


def drop_table(metadata, table_name):
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata

    del metadata[table_name]
    delete_table_data(table_name)

    print(f'Таблица "{table_name}" успешно удалена.')

    return metadata


def insert(metadata, table_name, values):
    if table_name not in metadata:
        raise ValueError(f'Таблица "{table_name}" не существует.')

    columns = metadata[table_name]
    user_columns = [col for col in columns if col.split(":")[0] != "ID"]

    if len(values) != len(user_columns):
        raise ValueError(
            f"Ожидалось {len(user_columns)} значений, "
            f"получено {len(values)}."
        )

    record = {}

    for column, value in zip(user_columns, values):
        name, data_type = column.split(":")

        expected_types = {
            "int": int,
            "str": str,
            "bool": bool,
        }

        expected_type = expected_types[data_type]

        # Используем type(), потому что bool является подклассом int.
        if type(value) is not expected_type:
            raise ValueError(
                f"Некорректное значение: {value!r}. "
                f"Столбец {name} ожидает тип {data_type}."
            )

        record[name] = value

    table_data = load_table_data(table_name)

    new_id = max((row["ID"] for row in table_data), default=0) + 1

    record = {"ID": new_id, **record}
    table_data.append(record)

    print(
        f'Запись с ID={new_id} успешно добавлена '
        f'в таблицу "{table_name}".'
    )

    return table_data


def select(table_data, where_clause=None):
    if where_clause is None:
        return table_data

    return [
        row for row in table_data
        if all(row.get(key) == value for key, value in where_clause.items())
    ]


def update(table_data, set_clause, where_clause):
    updated_data = []
    updated_ids = []

    for row in table_data:
        new_row = row.copy()

        if all(
            row.get(key) == value
            for key, value in where_clause.items()
        ):
            new_row.update(set_clause)
            updated_ids.append(row["ID"])

        updated_data.append(new_row)

    return updated_data, updated_ids


def delete(table_data, where_clause):
    deleted_ids = []
    remaining_data = []

    for row in table_data:
        if all(
            row.get(key) == value
            for key, value in where_clause.items()
        ):
            deleted_ids.append(row["ID"])
        else:
            remaining_data.append(row)

    return remaining_data, deleted_ids
