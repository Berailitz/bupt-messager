#!/usr/env/python3
# -*- coding: UTF-8 -*-

import logging
from ..bupt_messager.notice_manager.http_client import HTTPClient
from ..bupt_messager.notice_manager.notice_manager import NoticeManager
from ..bupt_messager.queued_bot import create_queued_bot
from ..bupt_messager.sql_handler import SQLHandler
from ..bupt_messager.mess import get_current_time, set_logger


def notice_manager_test(http_client=None):
    set_logger(
        f'log/test/notice_manager_test_{get_current_time()}.txt',
        console_level=logging.DEBUG,
        file_level=logging.DEBUG)
    http_client = http_client or HTTPClient()
    sql_handler = SQLHandler()
    queued_bot = create_queued_bot()
    notice_manager = NoticeManager(
        sql_handler=sql_handler, bot=queued_bot, http_client=http_client)
    notice_manager.start()
    return notice_manager


if __name__ == '__main__':
    notice_manager_test()
