"""Describe backend logic."""
import logging
import telegram
from datetime import datetime, timedelta
from ..config import BOT_NOTICE_LIST_LENGTH, BOT_STATUS_LIST_LENGTH, BOT_STATUS_STATISTIC_HOUR, STATUS_SYNCED
from ..mess import try_int
from .backend_helper import admin_only, BackendHelper

class BotBackend(object):
    """Backend logic.

    :member sql_handle: Attached :obj:SQLHadnle.
    :type sql_handle: SQLHadnle.
    :member updater: Active updater.
    :type updater: telegram.ext.Updater.
    """
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
        """Say Welcome when receiving command `/start`.
        """
        bot.send_message(chat_id=update.message.chat_id, text="Welcome.")
        insert_result = self.sql_handle.insert_chat(update.message.chat_id)
        if insert_result is not None:
            logging.info(f'BotBackend.start_command: new chat `{insert_result.id}`.')

    def latest_command(self, bot, update, args):
        """Say latest notices when receiving command `/latest {length}`.
        """
        try:
            length = int(args[0]) if args else BOT_NOTICE_LIST_LENGTH
        except ValueError as identifier:
            bot.send_message(chat_id=update.message.chat_id, text="Didn't understand...")
            logging.info(f'BotBackend.latest_command: {identifier}')
            return
        self.backend_helper.send_latest_notice(bot=bot, message=update.message, length=length, start=0)

    def latest_callback(self, bot, update):
        """Say latest notices list when receiving callback `latest_{length}_{start}`.
        """
        args = self.backend_helper.prase_callback(update)
        length = try_int(args[0]) if args else 1
        start = try_int(args[1]) if args[1:] else 0
        self.backend_helper.send_latest_notice(bot=bot, message=update.callback_query.message, length=length, start=start)
        update.callback_query.answer()

    @staticmethod
    def yo_command(bot, update):
        """Say yo notices when receiving command `/yo`.
        """
        bot.send_message(chat_id=update.message.chat_id, text='Yo~')

    @admin_only
    def restart_command(self, bot, update, args):
        """Restart when receiving command `/restart {start_arguments}`.
        """
        update.message.reply_text('Bot is restarting...')
        logging.warning(f'BotBackend: Restart command `{args}` from `{update.effective_user.name}`.')
        self.backend_helper.restart_app(args)

    def status_command(self, bot, update, args):
        """Send latest status list when receiving command `/status {length}`.
        """
        try:
            length = int(args[0]) if args else BOT_STATUS_LIST_LENGTH
        except ValueError as identifier:
            bot.send_message(chat_id=update.message.chat_id, text="Didn't understand...")
            logging.info(f'BotBackend.status_command: {identifier}')
            return
        latest_records = self.sql_handle.get_latest_status(datetime.now() - timedelta(hours=BOT_STATUS_STATISTIC_HOUR))
        error_records = [record for record in latest_records if record.status != STATUS_SYNCED] if latest_records else []
        error_rate = len(error_records) / len(latest_records) if latest_records else 0
        text = ""
        for status in latest_records[-length:]:
            text += f'{status.time}: {status.status_text}\n'
        text += f'Error rate: {100 * error_rate:.2f}%.'
        bot.send_message(chat_id=update.message.chat_id, text=text)

    def read_command(self, bot, update, args):
        """Send a notice when receiving command `/read {index}`.
        """
        index = try_int(args[0]) if args else 1
        self.backend_helper.send_notice(bot, update.message, index - 1)

    def read_callback(self, bot, update):
        """Send a notice when receiving callback `/read_{index}`.
        """
        args = self.backend_helper.prase_callback(update)
        index = try_int(args[0]) if args else 0
        self.backend_helper.send_notice(bot, update.callback_query.message, index)
        update.callback_query.answer()

    @staticmethod
    def unknown_command(bot, update):
        """Response when receiving unknown commands.
        """
        bot.send_message(chat_id=update.message.chat_id, text="Didn't understand...")
