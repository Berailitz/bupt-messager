#!/usr/env/python3
# -*- coding: UTF-8 -*-

import logging
from ..bupt_messager.notice_manager.http_client import HTTPClient
from ..bupt_messager.mess import get_current_time, set_logger
from ..bupt_messager.notice_manager.login_helper.auth_helper import AuthHelper
from ..bupt_messager.notice_manager.login_helper.web_vpn_helper import WebVPNHelper


def login_test(http_client=None):
    set_logger(
        f'log/test/login_test_{get_current_time()}.txt',
        console_level=logging.DEBUG,
        file_level=logging.DEBUG)
    http_client = http_client or HTTPClient()
    webvpn_helper = WebVPNHelper(http_client)
    auth_helper = AuthHelper(http_client)
    webvpn_helper.do_login()
    auth_helper.do_login()


if __name__ == '__main__':
    login_test()
