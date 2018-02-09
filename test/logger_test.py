import logging
import time
from ..bupt_messager.mess import get_current_time, set_logger


def logger_test():
    set_logger(
        f'log/test/logger_test.txt',
        console_level=logging.DEBUG,
        file_level=logging.DEBUG)
    counter = 0
    while True:
        logging.info(f'Counter: {counter}')
        counter += 1
        time.sleep(1)


if __name__ == '__main__':
    logger_test()
