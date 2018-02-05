#!/usr/env/python3
# -*- coding: UTF-8 -*-

import logging
from ..bupt_messager.notice_manager.bot_helper.bot_helper import BotHelper
from ..bupt_messager.sql_handle import SQLHandle
from ..bupt_messager.mess import get_current_time, set_logger

def bot_helper_test(http_client=None):
    sample_notice = {
        'summary': 'This is a summary.',
        'title': 'This is a Title.',
        'url': 'https://ohhere.xyz'
    }
    test_count = 20
    set_logger(f'log/test/bot_helper_test_{get_current_time}.txt', console_level=logging.DEBUG, file_level=logging.DEBUG)
    sql_handle = SQLHandle()
    bot_helper = BotHelper(sql_handle)
    for i in range(test_count):
        logging.info(f'Broadcast test: {i} / {test_count}.')
        bot_helper.broadcast_notice(sample_notice)

if __name__ == '__main__':
    bot_helper_test()
