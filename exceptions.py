class ConnectApiError(Exception):
    """Ошибка соединения с API."""

    pass


class MainError(Exception):
    """Ошибка в основном теле цикла."""

    pass


class StatusError(Exception):
    """Недокументированный статус домашней работы либо домашку без статуса."""

    pass


class NotHomeworkName(Exception):
    """Нет homework_name в homework."""

    pass
