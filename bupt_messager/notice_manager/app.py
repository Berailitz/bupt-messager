from .http_client import HTTPClient
from .notice_manager import NoticeManager
from ..sql_handle import SQLHandle

def create_app():
    http_client = HTTPClient()
    sql_handle = SQLHandle()
    notice_manager = NoticeManager(http_client, sql_handle)
    return notice_manager
