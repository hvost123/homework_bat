class EnvironmentError(Exception):
    """Нет обязательных токенов."""

    pass


class ConnectApiError(Exception):
    """Ошибка соединения с API."""

    pass


class TypeApiError(Exception):
    """Неверный тип данных API."""

    pass


class ValueApiError(Exception):
    """Отсутствуют данные в API."""

    pass


class TypeNotList(Exception):
    """Тип данных не соответствует списку."""

    pass


class TypeNotInt(Exception):
    """Время не целое число."""

    pass


class MainError(Exception):
    """Ошибка в основном теле цикла."""

    pass
