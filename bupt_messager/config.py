"""config of this app"""
#!/usr/env/python3
# -*- coding: UTF-8 -*-

try:
    from .credentials import *
except ImportError as credentials_import_error:
    print(credentials_import_error.msg)
    credentials_import_error.msg = "Failed to import credentials. Please make sure `credentials.py` exists."
    raise credentials_import_error

WEB_VPN_ALLOW_ERROR = True
NOTICE_TITLE_LENGTH = 80
NOTICE_SUMMARY_LENGTH = 200
ATTACHMENT_NAME_LENGTH = 50
NOTICE_CHECK_INTERVAL = 3600
BOT_BROADCAST_INTERVAL = 0.05
BOT_NOTICE_LIST_LENGTH = 5
