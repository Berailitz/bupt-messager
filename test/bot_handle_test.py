#!/usr/env/python3
# -*- coding: UTF-8 -*-

import logging
from ..bupt_messager.bot_handle.bot_handle import BotHandle
from ..bupt_messager.queued_bot import create_queued_bot
from ..bupt_messager.sql_handle import SQLManager
from ..bupt_messager.mess import get_current_time, set_logger

def bot_handle_test():
    set_logger(f'log/test/bot_helper_test_{get_current_time()}.txt', console_level=logging.DEBUG, file_level=logging.DEBUG)
    queued_bot = create_queued_bot()
    sql_manager = SQLManager()
    bot_handle = BotHandle(sql_manager=sql_manager, bot=queued_bot)
    bot_handle.add_handler()
    bot_handle.start()
    return bot_handle

if __name__ == '__main__':
    bot_handle_test()
