"""Utils."""
import datetime
import functools
import itertools
import logging
import logging.handlers
import threading
import time
from typing import Callable
from .config import LOG_MAX_TEXT_LENGTH


get_current_time = lambda: time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))


def fun_logger(*, prefix='Fun_logger: ', log_fun=logging.info):
    """Log function calls.

    :param log_fun: Callback function to save log, defaults to logging.
    :type log_fun: Callable, optional.
    :return: Text as the prefix of logs.
    :rtype: str.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            log_fun(f'{prefix}{func.__name__} called with `{str(args)[:LOG_MAX_TEXT_LENGTH]}`, `{str(kw)[:LOG_MAX_TEXT_LENGTH]}`.')
            result = func(*args, **kw)
            log_fun(f'{prefix}{func.__name__} returns `{str(result)[:LOG_MAX_TEXT_LENGTH]}`,')
            return result
        return wrapper
    return decorator


def set_logger(log_file_path: str, console_level=logging.INFO, file_level=logging.INFO):
    """Initialize logging module.

    :param log_file_path: Path of the log file.
    :type log_file_path: str.
    """
    prefix_format = '[%(levelname)s] %(asctime)s %(filename)s:%(lineno)d %(message)s'
    date_format = '%Y %b %d %H:%M:%S'
    rotation_time = datetime.time(hour=4)
    logging.basicConfig(
        level=console_level,
        format=prefix_format,
        datefmt=date_format,
    )
    file_hanfler = logging.handlers.TimedRotatingFileHandler(
        filename=log_file_path,
        when='midnight',
        interval=1,
        backupCount=10,
        atTime=rotation_time
    )
    file_hanfler.setLevel(file_level)
    formatter = logging.Formatter(fmt=prefix_format, datefmt=date_format)
    file_hanfler.setFormatter(formatter)
    logging.getLogger(name=None).addHandler(file_hanfler)
    logging.info("Start ....")


def try_int(text, default=None):
    """Try to convert `text` to an int, return `default` if failed.

    :param text: Target text.
    :type text: str.
    :param default: Default value, defaults to None.
    :type default: Any, optional.
    """
    try:
        return int(text)
    except ValueError:
        return default


def get_arg(target: type, args: list, kwargs: dict):
    """Select argument with type `target` in `args` and kwargs.

    :param target: Target type.
    :type target: type.
    :param args: Argument list.
    :type args: list.
    :param kwargs: keyword arguments.
    :type kwargs: dict.
    :raises ValueError: No such value with type `target`.
    :return: The first value with type `target`.
    :rtype: :obj:type.
    """
    for value in itertools.chain(args, kwargs.values()):
        if isinstance(value, target):
            return value
    raise ValueError(f'No such value: {target}')


def threaded(target_function: Callable) -> threading.Thread:
    """Start a function in another thread and return it.

    :return: New thread.
    :rtype: :obj:threading.Thread.
    """
    def wrapper(*args, **kwargs):
        """See `threaded`."""
        thread = threading.Thread(target=target_function, args=args, kwargs=kwargs)
        thread.start()
        return thread
    return wrapper
