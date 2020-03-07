"""Configs of this app."""
#!/usr/env/python3
# -*- coding: UTF-8 -*-

try:
    from .credentials import *
except ImportError as credentials_import_error:
    print(credentials_import_error.args)
    raise ImportError("Failed to import credentials. Please make sure `credentials.py` exists.")

LOG_MAX_TEXT_LENGTH = 2000
HTTP_CLIENT_MAX_RETRIES = 4
HTTP_CLIENT_TIME_OUT = 10
HTTP_CLIENT_REFERER = 'http://my.bupt.edu.cn/index.portal'
LOGIN_MAX_ATTEMPT = 3
LOGIN_WAIT_INTERVEL = 5
WEB_VPN_ALLOW_ERROR = True
PAGE_COUNTER_PER_UPDATE = 3
NOTICE_AUTHOR_LENGTH = 40
NOTICE_DOWNLOAD_INTERVAL = 5
NOTICE_TITLE_LENGTH = 80
NOTICE_DB_SUMMARY_LENGTH = 10000
NOTICE_MESSAGE_SUMMARY_LENGTH = 200
NOTICE_UPDATE_ERROR_SLEEP_TIME = 3600
ATTACHMENT_NAME_LENGTH = 50
NOTICE_CHECK_INTERVAL = 600
BROADCAST_CYCLE = 60 * 60 / NOTICE_CHECK_INTERVAL
BOT_NOTICE_LIST_LENGTH = 5
BOT_NOTICE_MAX_BUTTON_PER_LINE = 5
BOT_ALL_BURST_LIMIT = 15
BOT_GROUP_BURST_LIMIT = 10
BOT_STATUS_LIST_LENGTH = 5
BOT_RESTART_ARG_NO_ARG = 'no-arg'
BOT_START_VALID_ARGS = ['debug', 'no-bot', 'no-spider']
BOT_STATUS_STATISTIC_HOUR = 24
MESSAGER_PRINT_INTERVAL = 1200
STATUS_TEXT_DICT = {0: 'SYNCED', 1: 'ERROR-LOGIN-WEBVPN', 2: 'ERROR-LOGIN-AUTH', 3: 'ERROR-DOWNLOAD'}
STATUS_SYNCED = 0
STATUS_ERROR_LOGIN_WEBVPN = 1
STATUS_ERROR_LOGIN_AUTH = 2
STATUS_ERROR_DOWNLOAD = 3
MESSAGE_ABOUT_ME = "I'm a bot that forwards notifications." + \
    " 🍴 me at [https://github.com/Berailitz/bupt-messager](https://github.com/Berailitz/bupt-messager)."
NOTICE_TEXT = "*{title}*\n{summary}...(`{id}`@{datetime})"
NO_NOTICE_TEXT = "No such notice '{notice_index}'."
ERROR_NOTICE_TEXT = "Oops...something was wrong."
