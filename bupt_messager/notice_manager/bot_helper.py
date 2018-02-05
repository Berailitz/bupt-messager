import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from ..bupt_messager import queued_bot

class BotHelper(object):
    def __init__(self, sql_handle):
        self.bot = queued_bot
        self.sql_handle = sql_handle

    def broadcast_notice(self, notice_dict):
        keyboard = [[InlineKeyboardButton('READ', notice_dict['url'])]]
        menu_markup = InlineKeyboardMarkup(keyboard)
        chat_id_list = self.sql_handle.get_chat_ids()
        for chat_id in chat_id_list:
            self.bot.send_message(chat_id=chat_id, text=f"{notice_dict['title']}\n{notice_dict['summary']}", reply_markup=menu_markup)
        logging.info(f'Broadcast to {len(chat_id_list)} subscribers.')
