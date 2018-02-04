import os
from .mess import get_current_time
from .notice_manager import app as notice_manager_app
from .bot_handle.bot_handle import BotHandle
from .sql_handle import SQLManager

class BUPTMessager(object):
    def __init__(self):
        sql_manager = SQLManager()
        self.notice_manager = notice_manager_app.create_app(sql_manager)
        self.bot_handle = BotHandle(sql_manager)

    def run(self, log_path='log'):
        if not os.path.exists(log_path):
            raise FileNotFoundError(f'Log path does not exist: `{log_path}`.')
        log_path = f'{log_path}/log_{get_current_time()}.txt'
        self.notice_manager.start()
        self.bot_handle.start()

    def stop(self):
        self.notice_manager.stop()
        self.notice_manager.join()
        self.bot_handle.stop()
