import json
from pathlib import Path

DATA_DIR = Path("data")


def load_metadata(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_metadata(filepath, data):
    filepath = Path(filepath)

    filepath.parent.mkdir(parents=True, exist_ok=True)

    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def load_table_data(table_name):
    filepath = DATA_DIR / f"{table_name}.json"

    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def save_table_data(table_name, data):
    filepath = DATA_DIR / f"{table_name}.json"

    save_metadata(filepath, data)


def delete_table_data(table_name):
    filepath = DATA_DIR / f"{table_name}.json"

    filepath.unlink(missing_ok=True)
