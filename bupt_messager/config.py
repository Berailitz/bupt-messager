"""config of this app"""
#!/usr/env/python3
# -*- coding: UTF-8 -*-

try:
    from .credentials import *
except ImportError as credentials_import_error:
    print(credentials_import_error.msg)
    credentials_import_error.msg = "Failed to import credentials. Please make sure `credentials.py` exists."
    raise credentials_import_error

HTTP_CLIENT_MAX_RETRIES = 4
HTTP_CLIENT_TIME_OUT = 10
HTTP_CLIENT_REFERER = 'http://my.bupt.edu.cn/index.portal'
LOGIN_MAX_ATTEMPT = 3
LOGIN_WAIT_INTERVEL = 5
WEB_VPN_ALLOW_ERROR = True
NOTICE_DOWNLOAD_INTERVAL = 5
NOTICE_TITLE_LENGTH = 80
NOTICE_SUMMARY_LENGTH = 200
NOTICE_UPDATE_ERROR_SLEEP_TIME = 3600
ATTACHMENT_NAME_LENGTH = 50
NOTICE_CHECK_INTERVAL = 600
BOT_NOTICE_LIST_LENGTH = 5
BOT_NOTICE_MAX_BUTTON_PER_LINE = 5
BOT_ALL_BURST_LIMIT = 15
BOT_GROUP_BURST_LIMIT = 10
BOT_STATUS_LIST_LENGTH = 5
BOT_RESTART_ARG_NO_ARG = 'no-arg'
BOT_START_VALID_ARGS = ['debug', 'no-bot', 'no-spider']
MESSAGER_PRINT_INTERVAL = 1200
STATUS_TEXT_DICT = {0: 'SYNCED', 1: 'ERROR-LOGIN-WEBVPN', 2: 'ERROR-LOGIN-AUTH', 3: 'ERROR-DOWNLOAD'}
STATUS_SYNCED = 0
STATUS_ERROR_LOGIN_WEBVPN = 1
STATUS_ERROR_LOGIN_AUTH = 2
STATUS_ERROR_DOWNLOAD = 3
