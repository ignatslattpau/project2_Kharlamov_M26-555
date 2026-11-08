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

    # Если пользователь не указал ID, добавляем его автоматически.
    if "ID" not in column_names:
        new_columns.insert(0, "ID:int")
    else:
        new_columns.remove("ID:int")
        new_columns.insert(0, "ID:int")

    metadata[table_name] = new_columns

    columns_text = ", ".join(new_columns)

    print(
        f'Таблица "{table_name}" успешно создана '
        f"со столбцами: {columns_text}"
    )

    return metadata


def drop_table(metadata, table_name):
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata

    del metadata[table_name]

    print(f'Таблица "{table_name}" успешно удалена.')

    return metadata