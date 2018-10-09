"""Tools for the bot."""
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from ..models import Notification
from ..notice_helper import send_notice


class BotHelper(object):
    """Bot layer for `NoticeManager`.
    """

    def __init__(self, sql_handler=None, bot=None):
        self.bot = bot
        self.sql_handler = sql_handler

    def init_bot(self, bot=None):
        self.bot = bot

    def init_sql_handle(self, sql_handler=None):
        self.sql_handler = sql_handler

    def broadcast_notice(self, notice: Notification):
        """Broadcast new notification to all user.

        :param notice: New notification.
        """
        chat_id_list = self.sql_handler.get_chat_ids()
        logging.info(f'BotHelper: Broadcast to {len(chat_id_list)} subscribers.')
        for chat_id in chat_id_list:
            send_notice(self.bot, chat_id, notice)
