import re


def parse_value(value):
    value = value.strip()

    if (
        len(value) >= 2
        and value[0] == value[-1]
        and value[0] in ("'", '"')
    ):
        return value[1:-1]

    if value.lower() == "true":
        return True

    if value.lower() == "false":
        return False

    if re.fullmatch(r"-?\d+", value):
        return int(value)

    raise ValueError(
        f"Некорректное значение: {value}. Попробуйте снова."
    )


def parse_values(text):
    parts = []
    current = []
    quote = None
    escaped = False

    for char in text:
        if escaped:
            current.append(char)
            escaped = False
            continue

        if char == "\\" and quote is not None:
            current.append(char)
            escaped = True
            continue

        if char in ("'", '"'):
            if quote is None:
                quote = char
            elif quote == char:
                quote = None

        if char == "," and quote is None:
            parts.append("".join(current).strip())
            current = []
        else:
            current.append(char)

    if quote is not None:
        raise ValueError("Ошибка: Незакрытые кавычки.")

    parts.append("".join(current).strip())

    return [parse_value(part) for part in parts]


def parse_condition(text):
    match = re.fullmatch(r"\s*(\w+)\s*=\s*(.+?)\s*", text)

    if match is None:
        raise ValueError(
            f"Некорректное условие: {text}. "
            "Используйте формат столбец = значение."
        )

    column_name = match.group(1)
    value = parse_value(match.group(2))

    return {column_name: value}
