"""Credentials of this app."""
#!/usr/env/python3
# -*- coding: UTF-8 -*-

from typing import List

PROXY_URL = None
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://username:password@host/database?charset=utf8mb4'
BOT_LISTEN_ADDRESS = '0.0.0.0'
BOT_WEB_HOOK_PORT = '443'
BOT_WEB_HOOK_URL = 'https://domain.tdl/path'
BOT_WEB_HOOK_URL_PATH = 'path'
BOT_CERT_PATH = None # type: str
BOT_KEY_PATH = None # type: str
BOT_TOKEN = 'id:token'
BOT_ADMIN_IDS = [] # type: List[int]
WEB_VPN_USERNAME = 'username'
WEB_VPN_PASSWORD = 'password'
AUTH_USERNAME = 'username'
AUTH_PASSWORD = 'password'
TESSERACT_CMD = None
