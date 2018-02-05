import logging
from telegram import ParseMode
from ..config import BOT_NOTICE_LIST_LENGTH

class BotBackend(object):
    def __init__(self, sql_handle=None):
        self.sql_handle = sql_handle

    def init_sql_handle(self, sql_handle):
        self.sql_handle = sql_handle

    def start_command(self, bot, update):
        bot.send_message(chat_id=update.message.chat_id, text="Welcome.")
        insert_result = self.sql_handle.insert_chat(update.message.chat_id)
        if insert_result is not None:
            logging.info(f'BotBackend.start_command: new chat `{insert_result.id}`.')

    def latest_command(self, bot, update, args):
        try:
            length = int(args[0]) if args else BOT_NOTICE_LIST_LENGTH
        except ValueError as identifier:
            bot.send_message(chat_id=update.message.chat_id, text="Didn't understand...", parse_mode=ParseMode.MARKDOWN)
            logging.info(f'BotBackend.latest_command: {identifier}')
            return
        text = ""
        for index, notice in enumerate(self.sql_handle.get_latest_notices(length)):
            text += f'{index + 1}.[{notice.title}]({notice.url})\n'
        bot.send_message(chat_id=update.message.chat_id, text=text, parse_mode=ParseMode.MARKDOWN)

    def yo_command(self, bot, update):
        bot.send_message(chat_id=update.message.chat_id, text='Yo~')
