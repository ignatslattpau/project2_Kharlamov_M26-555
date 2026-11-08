import json
from pathlib import Path

from primitive_db.constants import DATA_DIR

DATA_DIR = Path(DATA_DIR)


def load_metadata(filepath):
    """Загружает метаданные из JSON-файла или возвращает пустой словарь."""
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_metadata(filepath, data):
    """Сохраняет переданные данные в JSON-файл."""
    filepath = Path(filepath)

    filepath.parent.mkdir(parents=True, exist_ok=True)

    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def load_table_data(table_name):
    """Загружает записи таблицы из JSON-файла или возвращает пустой список."""
    filepath = DATA_DIR / f"{table_name}.json"

    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def save_table_data(table_name, data):
    """Сохраняет записи таблицы в отдельный JSON-файл."""
    filepath = DATA_DIR / f"{table_name}.json"

    save_metadata(filepath, data)


def delete_table_data(table_name):
    """Удаляет JSON-файл с данными указанной таблицы."""
    filepath = DATA_DIR / f"{table_name}.json"

    filepath.unlink(missing_ok=True)
