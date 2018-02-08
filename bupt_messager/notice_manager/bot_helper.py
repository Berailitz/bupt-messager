import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

class BotHelper(object):
    def __init__(self, sql_handle=None, bot=None):
        self.bot = bot
        self.sql_handle = sql_handle

    def init_bot(self, bot=None):
        self.bot = bot

    def init_sql_handle(self, sql_handle=None):
        self.sql_handle = sql_handle

    def broadcast_notice(self, notice_dict):
        keyboard = [[InlineKeyboardButton('READ', notice_dict['url'])]]
        menu_markup = InlineKeyboardMarkup(keyboard)
        chat_id_list = self.sql_handle.get_chat_ids()
        for chat_id in chat_id_list:
            self.bot.send_message(chat_id=chat_id, text=f"*{notice_dict['title']}*\n{notice_dict['summary']}", reply_markup=menu_markup)
        logging.info(f'BotHelper: Broadcast to {len(chat_id_list)} subscribers.')
