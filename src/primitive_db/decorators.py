import time
from functools import wraps

import prompt


def handle_db_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        except FileNotFoundError:
            print("Ошибка: Файл данных не найден.")

        except KeyError as error:
            print(f"Ошибка: Таблица или столбец {error} не найден.")

        except ValueError as error:
            print(f"Ошибка валидации: {error}")

        return None

    return wrapper


def confirm_action(action_name):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            answer = prompt.string(
                f'Вы уверены, что хотите выполнить '
                f'"{action_name}"? [y/n]: '
            )

            if answer.strip().lower() != "y":
                print("Операция отменена.")
                return None

            return func(*args, **kwargs)

        return wrapper

    return decorator


def log_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.monotonic()

        try:
            return func(*args, **kwargs)
        finally:
            elapsed = time.monotonic() - start
            print(
                f"Функция {func.__name__} "
                f"выполнилась за {elapsed:.3f} секунд"
            )

    return wrapper



def create_cacher():
    cache = {}

    def cache_result(key, value_func):
        if key in cache:
            return cache[key]

        result = value_func()
        cache[key] = result

        return result

    return cache_result
