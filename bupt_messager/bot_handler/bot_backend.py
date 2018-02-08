import logging
from threading import Thread
from telegram import ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from ..config import BOT_NOTICE_LIST_LENGTH, BOT_STATUS_LIST_LENGTH
from ..mess import try_int
from .backend_helper import admin_only, BackendHelper

class BotBackend(object):
    def __init__(self, *, sql_handle=None, updater=None):
        self.sql_handle = sql_handle
        self.updater = updater
        self.backend_helper = BackendHelper(sql_handle=sql_handle, updater=updater)

    def init_sql_handle(self, sql_handle):
        self.sql_handle = sql_handle
        self.backend_helper.init_sql_handle(sql_handle)

    def init_updater(self, updater):
        self.updater = updater
        self.backend_helper.init_updater(updater)

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
        self.backend_helper.send_latest_notice(bot=bot, update=update, length=length, start=0)

    @staticmethod
    def yo_command(bot, update):
        bot.send_message(chat_id=update.message.chat_id, text='Yo~')

    @admin_only
    def restart_command(self, bot, update):
        update.message.reply_text('Bot is restarting...')
        logging.warning(f'BotBackend: Received restart command from user `{update.effective_user.name}`.')
        self.backend_helper.restart_app()

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
        self.send_notice(index, bot, update)

    def read_callback(self, bot, update):
        args = self.backend_helper.prase_callback(update)
        index = try_int(args[0]) if args else 1
        self.send_notice(index, bot, update)

    def send_notice(self, bot, update, index):
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
