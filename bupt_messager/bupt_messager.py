import logging
import os
import threading
import time
from .mess import get_current_time, set_logger
from .notice_manager import app as notice_manager_app
from .bot_handle.bot_handle import BotHandle
from .queued_bot import create_queued_bot
from .sql_handle import SQLManager

queued_bot = create_queued_bot()

class BUPTMessager(object):
    def __init__(self, debug_mode=False):
        sql_manager = SQLManager()
        self.debug_mode = debug_mode
        self.notice_manager = notice_manager_app.create_app(sql_manager)
        self.bot_handle = BotHandle(sql_manager)

    def run(self, log_folder='log'):
        if not os.path.exists(log_folder):
            raise FileNotFoundError(f'Log path does not exist: `{log_folder}`.')
        if self.debug_mode:
            log_filename = f'bupt_messager_{get_current_time()}_debug.log'
            log_path = os.path.join(log_folder, log_filename)
            set_logger(log_path, console_level=logging.DEBUG, file_level=logging.DEBUG)
        else:
            log_filename = f'bupt_messager_{get_current_time()}.log'
            log_path = os.path.join(log_folder, log_filename)
            set_logger(log_path, console_level=logging.INFO, file_level=logging.INFO)
        self.notice_manager.start()
        self.bot_handle.start()
        while True:
            logging.info(f'Workers: {threading.enumerate()}')
            time.sleep(60)

    def stop(self):
        self.notice_manager.stop()
        self.bot_handle.stop()
        self.notice_manager.join()
