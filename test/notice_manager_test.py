#!/usr/env/python3
# -*- coding: UTF-8 -*-

import logging
from ..bupt_messager.notice_manager.http_client import HTTPClient
from ..bupt_messager.notice_manager.notice_manager import NoticeManager
from ..bupt_messager.queued_bot import create_queued_bot
from ..bupt_messager.sql_handle import SQLHandle
from ..bupt_messager.mess import get_current_time, set_logger

def notice_manager_test(http_client=None):
    set_logger(f'log/test/notice_manager_test_{get_current_time()}.txt', console_level=logging.DEBUG, file_level=logging.DEBUG)
    http_client = http_client or HTTPClient()
    sql_handle = SQLHandle()
    queued_bot = create_queued_bot()
    notice_manager = NoticeManager(sql_handle=sql_handle, bot=queued_bot, http_client=http_client)
    notice_manager._login()
    notice_manager.update()

if __name__ == '__main__':
    notice_manager_test()
