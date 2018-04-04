"""Tools for the bot."""
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode


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

    def broadcast_notice(self, notice_dict: dict):
        """Broadcast new notification to all user.

        :param notice_dict: New notification.
        :type notice_dict: dict.
        """
        keyboard = [[InlineKeyboardButton('READ', notice_dict['url'])]]
        menu_markup = InlineKeyboardMarkup(keyboard)
        chat_id_list = self.sql_handler.get_chat_ids()
        for chat_id in chat_id_list:
            self.bot.send_message(
                chat_id=chat_id,
                text=f"*{notice_dict['title']}*\n{notice_dict['summary']}...({notice_dict['time'].strftime('%Y/%m/%d')})",
                reply_markup=menu_markup,
                parse_mode=ParseMode.MARKDOWN)
        logging.info(f'BotHelper: Broadcast to {len(chat_id_list)} subscribers.')
