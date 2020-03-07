"""Describe backend logic."""
import logging
from datetime import datetime, timedelta
from telegram import ParseMode
from telegram.error import TelegramError, Unauthorized, BadRequest, TimedOut, ChatMigrated, NetworkError
from ..config import BOT_NOTICE_LIST_LENGTH, BOT_STATUS_LIST_LENGTH, BOT_STATUS_STATISTIC_HOUR
from ..config import MESSAGE_ABOUT_ME, STATUS_SYNCED, ERROR_NOTICE_TEXT
from ..mess import try_int
from .backend_helper import admin_only, BackendHelper


class BotBackend(object):
    """Backend logic.

    :member sql_handler: Attached :obj:SQLHadnle.
    :type sql_handler: SQLHadnle.
    :member updater: Active updater.
    :type updater: telegram.ext.Updater.
    """
    def __init__(self, *, sql_handler=None, updater=None):
        self.sql_handler = sql_handler
        self.updater = updater
        self.backend_helper = BackendHelper(sql_handler=sql_handler, updater=updater)

    def init_sql_handle(self, sql_handler):
        self.sql_handler = sql_handler
        self.backend_helper.init_sql_handle(sql_handler)

    def init_updater(self, updater):
        self.updater = updater
        self.backend_helper.init_updater(updater)

    def about_command(self, bot, update):
        """Introduce myself, for `/about`.
        """
        bot.send_message(chat_id=update.message.chat_id, text=MESSAGE_ABOUT_ME, parse_mode=ParseMode.MARKDOWN)
        logging.info(f'BotBackend.about_command: From chat `{update.message.chat_id}`.')

    def start_command(self, bot, update):
        """Say Welcome when receiving command `/start`.
        """
        bot.send_message(chat_id=update.message.chat_id, text="Welcome.")
        logging.info(f'Started by chat `{update.message.chat_id}`.')
        insert_result_id = self.sql_handler.insert_chat(update.message.chat_id)
        if insert_result_id is not None:
            logging.info(f'BotBackend.start_command: new chat `{insert_result_id}`.')

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
        latest_records = self.sql_handler.get_latest_status(datetime.now() - timedelta(hours=BOT_STATUS_STATISTIC_HOUR))
        if latest_records:
            error_records = [record for record in latest_records if record.status != STATUS_SYNCED]
            error_rate = len(error_records) / len(latest_records)
            text = ""
            for status in latest_records[-length:]:
                text += f'{status.time}: {status.status_text}\n'
            text += f'Error rate: {100 * error_rate:.2f}%.'
        else:
            logging.warning('BotBackend: No status selected.')
            text = "No status log."
        bot.send_message(chat_id=update.message.chat_id, text=text)

    def read_command(self, bot, update, args):
        """Send a notice when receiving command `/read {index}`.
        """
        self.backend_helper.send_notice_by_id(bot, update.message.chat_id, args[0])

    def read_callback(self, bot, update):
        """Send a notice when receiving callback `/read_{index}`.
        """
        args = self.backend_helper.prase_callback(update)
        self.backend_helper.send_notice_by_id(bot, update.callback_query.message.chat_id, args[0])
        update.callback_query.answer()

    def error_collector(self, bot, error: Exception, *, chat_id: int = None) -> None:
        try:
            raise error
        except Unauthorized:
            # remove update.message.chat_id from conversation list
            if chat_id is None:
                raise error
            else:
                logging.warning(f"Remove Chat(id='{chat_id}')")
                self.sql_handler.remove_chat(chat_id)
        except BadRequest:
            # handle malformed requests - read more below!
            logging.error(f"Bad request detected. (chat_id=`{chat_id}`)")
        except TimedOut:
            # handle slow connection problems
            logging.error(f"Timeout detected. (chat_id=`{chat_id}`)")
        except NetworkError:
            # handle other connection problems
            logging.error(f"Network error detected. (chat_id=`{chat_id}`)")
        except ChatMigrated:
            # the chat_id of a group has changed, use error.new_chat_id instead
            logging.warning(f"Chat migrated detected, from `{chat_id}` to `{error.new_chat_id}`.")
            self.sql_handler.remove_chat(chat_id)
            self.sql_handler.insert_chat(error.new_chat_id)
        except Exception as identifier:
            logging.error(f"Unknown error. (chat_id=`{chat_id}`)")
            logging.exception(error)
            bot.send_error_report()
            bot.send_message(chat_id=chat_id, text=ERROR_NOTICE_TEXT)
            raise identifier

    def error_callback(self, bot, update, error: Exception):
        chat_id = update.message.chat_id
        self.error_collector(bot, error, chat_id=chat_id)

    @staticmethod
    def unknown_command(bot, update):
        """Response when receiving unknown commands.
        """
        bot.send_message(chat_id=update.message.chat_id, text="Didn't understand...")
