"""Main class."""
import logging
import os
import signal
import threading
import time
from .mess import set_logger
from .notice_manager.notice_manager import create_notice_manager
from .bot_handler.bot_handler import BotHandler
from .config import MESSAGER_PRINT_INTERVAL
from .queued_bot import create_queued_bot
from .sql_handler import SQLManager


class BUPTMessager(object):
    """Messager class, the controller.

    :type *_mode: bool.
    :type log_folder: str.
    """
    def __init__(self, *, debug_mode=False, no_bot_mode=False, no_spider_mode=False):
        sql_manager = SQLManager()
        self.debug_mode = debug_mode
        self.no_bot_mode = no_bot_mode
        self.no_spider_mode = no_spider_mode
        queued_bot = create_queued_bot()
        self.notice_manager = create_notice_manager(sql_manager=sql_manager, bot=queued_bot)
        self.bot_handler = BotHandler(sql_manager=sql_manager, bot=queued_bot)
        self.bot_handler.add_handler()
        self.log_folder = 'log'
        self._init_logger()
        queued_bot.set_error_handle(self.bot_handler.bot_backend.error_collector)
        signal.signal(signal.SIGINT, self.stop)
        signal.signal(signal.SIGTERM, self.stop)

    def _init_logger(self):
        if not os.path.exists(self.log_folder):
            raise FileNotFoundError(f'Log path does not exist: `{self.log_folder}`.')
        if self.debug_mode:
            log_filename = f'bupt_messager_{os.getpid()}_debug.log'
            log_path = os.path.join(self.log_folder, log_filename)
            set_logger(log_path, console_level=logging.DEBUG, file_level=logging.DEBUG)
        else:
            log_filename = f'bupt_messager_{os.getpid()}.log'
            log_path = os.path.join(self.log_folder, log_filename)
            set_logger(log_path, console_level=logging.INFO, file_level=logging.INFO)

    def start(self):
        """Start messager, reading attributes `*_mode`.
        """
        if self.no_spider_mode:
            logging.warning('BUPTMessager: no_spider_mode is ON.')
        else:
            self.notice_manager.start()
        if self.no_bot_mode:
            logging.warning('BUPTMessager: no_bot_mode is ON.')
        else:
            self.bot_handler.start()
        while True:
            logging.info(f'Workers: {threading.enumerate()}')
            time.sleep(MESSAGER_PRINT_INTERVAL)

    def stop(self, signum: int = None, frame=None):
        """Stop messager gracefully.

        :param signum: Number representing a signal, defaults to None
        :type signum: int, optional
        :param frame: Stack frame, defaults to None
        :type frame: Frame, optional
        """
        if signum:
            logging.warning(f'BUPTMessager: Stop due to signal: {signum}')
        if not self.no_bot_mode:
            self.bot_handler.stop()
        if not self.no_spider_mode:
            self.notice_manager.stop()
            self.notice_manager.join()
        self.bot_handler.stop_bot()
