import logging
import os
import threading
import time
from .mess import get_current_time, set_logger
from .notice_manager.app import create_notice_manager
from .bot_handle.bot_handle import BotHandle
from .config import MESSAGER_PRINT_INTERVAL
from .queued_bot import create_queued_bot
from .sql_handle import SQLManager

class BUPTMessager(object):
    def __init__(self, debug_mode=False):
        sql_manager = SQLManager()
        self.debug_mode = debug_mode
        queued_bot = create_queued_bot()
        self.notice_manager = create_notice_manager(sql_manager=sql_manager, bot=queued_bot)
        self.bot_handle = BotHandle(sql_manager=sql_manager, bot=queued_bot)
        self.bot_handle.add_handler()
        self.log_folder = 'log'

    def set_logger(self):
        if not os.path.exists(self.log_folder):
            raise FileNotFoundError(f'Log path does not exist: `{self.log_folder}`.')
        if self.debug_mode:
            log_filename = f'bupt_messager_{get_current_time()}_debug.log'
            log_path = os.path.join(self.log_folder, log_filename)
            set_logger(log_path, console_level=logging.DEBUG, file_level=logging.DEBUG)
        else:
            log_filename = f'bupt_messager_{get_current_time()}.log'
            log_path = os.path.join(self.log_folder, log_filename)
            set_logger(log_path, console_level=logging.INFO, file_level=logging.INFO)

    def _run(self):
        self.notice_manager.start()
        self.bot_handle.start()
        while True:
            logging.info(f'Workers: {threading.enumerate()}')
            time.sleep(MESSAGER_PRINT_INTERVAL)

    def start(self):
        self.set_logger()
        self._run()

    def stop(self):
        self.notice_manager.stop()
        self.bot_handle.stop()
        self.notice_manager.join()
