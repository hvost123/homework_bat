import os
import telegram
import requests
import sys
import logging
import time
from dotenv import load_dotenv
import exceptions
from http import HTTPStatus

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens():
    """Проверяет доступность переменных окружения."""
    message_error = 'Отсутствие обязательных переменных окружения.'
    try:
        test_con = all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID])
        if test_con:
            return test_con
        else:
            logging.critical(message_error)
            exit(message_error)
    except Exception:
        logging.critical(message_error)


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    message_send = 'Удачная отправка сообщения в Telegram.'
    message_error = 'Cбой при отправке сообщения в Telegram.'
    try:
        bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
        )
    except telegram.TelegramError:
        logging.error(message_error)
    else:
        logging.debug(message_send)


def get_api_answer(timestamp):
    """Делает запрос к единственному эндпоинту API-сервиса."""
    message = 'Отправка запроса к API-сервиса.'
    massage_error = 'Неверный ответ.'
    massage_respons = 'Hедоступность эндпоинта.'
    par_request = {
        'url': ENDPOINT,
        'headers': HEADERS,
        'params': {'from_date': timestamp},
    }
    logging.debug(message)
    try:
        homework_statuses = requests.get(**par_request)
        if homework_statuses.status_code != HTTPStatus.OK:
            logging.error(massage_respons)
            raise exceptions.InvalidResponse(massage_respons)
        return homework_statuses.json()
    except Exception:
        logging.error(massage_error)
        raise exceptions.ConnectApiError(massage_error)


def check_response(response):
    """Проверяет ответ API на соответствие документации."""
    error_type_api = 'Ошибка в типе ответа API.'
    empty_answer_apy = 'Пустой ответ от API.'
    no_list = 'Homeworks не является списком.'
    no_int = 'Current_date не является счислом.'

    if not isinstance(response, dict):
        logging.error(error_type_api)
        raise TypeError(error_type_api)
    if 'homeworks' not in response or 'current_date' not in response:
        logging.error(empty_answer_apy)
        raise TypeError(empty_answer_apy)
    if not isinstance(response['homeworks'], list):
        logging.error(no_list)
        raise TypeError(no_list)
    if not isinstance(response['current_date'], int):
        logging.error(no_int)
        raise TypeError(no_int)
    return response


def parse_status(homework):
    """Извлекает из информации статус этой работы."""
    if 'homework_name' not in homework:
        logging.error('Нет homework_name в homework.')
        raise exceptions.NotHomeworkName('Нет homework_name в homework.')
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    try:
        verdict = HOMEWORK_VERDICTS[homework_status]
    except Exception:
        logging.error('Недокументированный статус домашней работы.')
        raise exceptions.StatusError('Ошибочный статус.')
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)s] %(message)s',
        stream=sys.stdout
    )
    logging.info('Начало работы Бота')
    check_tokens()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    send_message(bot, 'Начало работы Бота')
    request = get_api_answer(timestamp)
    initial_answer = check_response(request)
    logging.info('Запрос API прошел проверку.')

    while True:
        try:
            request_new = get_api_answer(timestamp)
            verified_answer = check_response(request_new)
            if verified_answer != initial_answer:
                getting_answer = parse_status(verified_answer['homeworks'][0])
                send_message(bot, getting_answer)
                logging.info(f'Отправлен новый статус: {getting_answer}')
            else:
                logging.info('Статус не обновлен.')
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.info(message)
            raise exceptions.MainError('Ошибка при выполнении цикла.')
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
