"""Модуль с декораторами и конфигом для логирования"""
import time
from functools import wraps
import logging.config

logger = logging.getLogger('app_logger')


def backoff(exception_class, start_sleep_time=0.1, factor=2, border_sleep_time=10):
    """
    Функция для повторного выполнения функции через некоторое время, если возникла ошибка.
    Использует наивный экспоненциальный рост времени повтора (factor) до граничного времени ожидания (border_sleep_time)

    Формула:
        t = start_sleep_time * 2^(n) if t < border_sleep_time
        t = border_sleep_time if t >= border_sleep_time
    :param exception_class: класс ошибки
    :param start_sleep_time: начальное время повтора
    :param factor: во сколько раз нужно увеличить время ожидания
    :param border_sleep_time: граничное время ожидания
    :return: результат выполнения функции
    """

    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):

            t = start_sleep_time
            n = 0

            while True:
                try:
                    return func(*args, **kwargs)
                except exception_class as e:
                    logger.error(msg=e, exc_info=True)
                    time.sleep(t)
                    n += 1
                    t = start_sleep_time * factor ** n
                    if t > border_sleep_time:
                        t = border_sleep_time

        return inner

    return func_wrapper


def init_coroutine(coroutine):
    """Декоратор для инициализации корутин."""

    @wraps(coroutine)
    def wrapper(*args, **kwargs):
        _coroutine = coroutine(*args, **kwargs)
        next(_coroutine)
        return _coroutine

    return wrapper


class LoggingNoErrorFilter(logging.Filter):
    """Фильтр для логирования. Ошибки в stderr, остальные сообщения в stdout"""

    def __init__(self, param=None):
        super().__init__()
        self.param = param

    def filter(self, record):
        return record.levelno <= logging.WARNING


LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': True,
    'filters': {
        'no_error_filter': {
            '()': LoggingNoErrorFilter,
        }
    },
    'formatters': {
        'json_formatter': {
            'class': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s [%(levelname)s] %(name)s %(message)s ',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'json_formatter_for_errors': {
            'class': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': "%(asctime)s - [%(levelname)s] - %(name)s - %(filename)s) - %(funcName)s - %(lineno)d - %(message)s",
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },
    'handlers': {
        'stream_handler': {
            'level': 'DEBUG',
            'formatter': 'json_formatter',
            'filters': ['no_error_filter'],
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        },
        'stream_handler_errors': {
            'level': 'ERROR',
            'formatter': 'json_formatter_for_errors',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stderr',
        },
    },
    'loggers': {
        'app_logger': {
            'handlers': ['stream_handler', 'stream_handler_errors'],
            'level': 'DEBUG',
            'propagate': True,
        }
    },
}
