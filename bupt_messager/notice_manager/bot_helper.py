import logging
import time
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from ..config import BOT_BROADCAST_INTERVAL, BOT_TOKEN, PROXY_URL

class BotHelper(object):
    def __init__(self, sql_handle):
        my_request = telegram.utils.request.Request(proxy_url=PROXY_URL)
        self.bot = telegram.Bot(token=BOT_TOKEN, request=my_request)
        self.sql_handle = sql_handle

    def broadcast_notice(self, notice_dict):
        keyboard = [[InlineKeyboardButton('READ', notice_dict['url'])]]
        menu_markup = InlineKeyboardMarkup(keyboard)
        chat_list = self.sql_handle.get_chats()
        for chat_id in [chat.id for chat in chat_list]:
            self.bot.send_message(chat_id=chat_id, text=f"{notice_dict['title']}\n{notice_dict['text']}")
            time.sleep(BOT_BROADCAST_INTERVAL)
        logging.info(f'Broadcast to {len(chat_list)} subscribers.', reply_markup=menu_markup)
