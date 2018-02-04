from .http_client import HTTPClient
from .notice_manager import NoticeManager
from ..sql_handle import SQLHandle

def create_app(sql_manager):
    http_client = HTTPClient()
    sql_handle = SQLHandle(sql_manager)
    notice_manager = NoticeManager(http_client, sql_handle)
    return notice_manager
