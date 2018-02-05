import logging
import time

get_current_time = lambda: time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))

def set_logger(log_file_path, console_level=logging.INFO, file_level=logging.INFO):
    """set logger"""
    logging.basicConfig(
        level=file_level,
        format='[%(levelname)s] %(asctime)s %(filename)s:%(lineno)d %(message)s',
        datefmt='%Y %b %d %H:%M:%S',
        filename=log_file_path,
        filemode='a'
        )
    console = logging.StreamHandler()
    console.setLevel(console_level)
    formatter = logging.Formatter('[%(levelname)s] %(asctime)s %(filename)s:%(lineno)d %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)
    logging.info("Start ....")
