from telegram import ParseMode
from ..config import BOT_NOTICE_LIST_LENGTH

class Backend(object):
    def __init__(self, sql_handle=None):
        self.sql_handle = sql_handle

    def init_sql_handle(self, sql_handle):
        self.sql_handle = sql_handle

    def start_command(self, bot, update):
        bot.send_message(chat_id=update.message.chat_id, text="Welcome.")
        self.sql_handle.insert_chat(update.message.chat_id)

    def latest_command(self, bot, update, args):
        length = args[0] if args else BOT_NOTICE_LIST_LENGTH
        text = ""
        for index, notice in enumerate(self.sql_handle.get_latest_notices(length)):
            text += f'{index + 1}.[{notice.title}]({notice.url})\n'
        bot.send_message(chat_id=update.message.chat_id, text=text, parse_mode=ParseMode.MARKDOWN)

    def yo_command(self, bot, update):
        bot.send_message(chat_id=update.message.chat_id, text='Yo~')
