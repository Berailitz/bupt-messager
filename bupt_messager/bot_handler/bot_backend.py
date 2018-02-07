import logging
from telegram import ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from ..config import BOT_NOTICE_LIST_LENGTH, BOT_STATUS_LIST_LENGTH
from ..mess import try_int

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
            bot.send_message(chat_id=update.message.chat_id, text="Didn't understand...")
            logging.info(f'BotBackend.latest_command: {identifier}')
            return
        text = ""
        for index, notice in enumerate(self.sql_handle.get_latest_notices(length)):
            text += f'{index + 1}.[{notice.title}]({notice.url})({notice.date})\n'
        bot.send_message(chat_id=update.message.chat_id, text=text, parse_mode=ParseMode.MARKDOWN)

    @staticmethod
    def yo_command(bot, update):
        bot.send_message(chat_id=update.message.chat_id, text='Yo~')

    def status_command(self, bot, update, args):
        try:
            length = int(args[0]) if args else BOT_STATUS_LIST_LENGTH
        except ValueError as identifier:
            bot.send_message(chat_id=update.message.chat_id, text="Didn't understand...")
            logging.info(f'BotBackend.status_command: {identifier}')
            return
        text = ""
        for status in self.sql_handle.get_latest_status(length):
            text += f'{status.time}: {status.status_text}\n'
        bot.send_message(chat_id=update.message.chat_id, text=text)

    def read_command(self, bot, update, args):
        index = try_int(args[0]) if args else 1
        notice_list = self.sql_handle.get_latest_notices(length=1, start=index - 1)
        if notice_list:
            target_notice = notice_list[0]
            self._send_notice(bot, target_notice=target_notice, chat_id=update.message.chat_id)
        else:
            bot.send_message(chat_id=update.message.chat_id, text="No such notice.")

    @staticmethod
    def _send_notice(bot, *, target_notice, chat_id):
        keyboard = [[InlineKeyboardButton('READ', target_notice.url)]]
        menu_markup = InlineKeyboardMarkup(keyboard)
        bot.send_message(
            chat_id=chat_id,
            text=f"{target_notice.title}\n{target_notice.summary}",
            reply_markup=menu_markup
        )

    @staticmethod
    def unknown_command(bot, update):
        bot.send_message(chat_id=update.message.chat_id, text="Didn't understand...")
