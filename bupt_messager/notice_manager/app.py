from .notice_manager import NoticeManager
from ..sql_handle import SQLHandle

def create_notice_manager(sql_manager, bot):
    sql_handle = SQLHandle(sql_manager)
    notice_manager = NoticeManager(sql_handle=sql_handle, bot=bot)
    return notice_manager
