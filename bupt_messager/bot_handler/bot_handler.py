import logging
from telegram.ext import Filters, Updater, CallbackQueryHandler, CommandHandler, MessageHandler
from ..config import BOT_CERT_PATH, BOT_KEY_PATH, BOT_LISTEN_ADDRESS, BOT_WEB_HOOK_PORT, BOT_WEB_HOOK_URL, BOT_WEB_HOOK_URL_PATH
from ..sql_handler import SQLHandler
from .bot_backend import BotBackend


class BotHandler(object):
    """Register backend logic.

    :member bot_backend: Attached :obj:BotBackend.
    :type bot_backend: BotBackend.
    :member updater: Active updater.
    :type updater: telegram.ext.Updater.
    """
    def __init__(self, sql_manager=None, bot=None):
        self.bot = bot
        self.updater = Updater(bot=bot) if bot else None
        self.bot_backend = BotBackend(
            sql_handler=SQLHandler(sql_manager=sql_manager),
            updater=self.updater
        )

    def init_bot_backend(self, sql_manager):
        self.bot_backend.sql_handler.init_sql_manager(sql_manager)

    def init_updater(self, bot):
        self.updater = Updater(bot=bot)

    def add_handler(self):
        """Register handlers, run once per start.
        """
        dispatcher = self.updater.dispatcher
        about_handler = CommandHandler('about', self.bot_backend.about_command)
        dispatcher.add_handler(about_handler)
        start_handler = CommandHandler('start', self.bot_backend.start_command)
        dispatcher.add_handler(start_handler)
        latest_handler = CommandHandler('latest', self.bot_backend.latest_command, pass_args=True)
        dispatcher.add_handler(latest_handler)
        latest_callback = CallbackQueryHandler(pattern='^latest_', callback=self.bot_backend.latest_callback)
        dispatcher.add_handler(latest_callback)
        status_handler = CommandHandler('status', self.bot_backend.status_command, pass_args=True)
        dispatcher.add_handler(status_handler)
        read_handler = CommandHandler('read', self.bot_backend.read_command, pass_args=True)
        dispatcher.add_handler(read_handler)
        read_callback = CallbackQueryHandler(pattern='^read_', callback=self.bot_backend.read_callback)
        dispatcher.add_handler(read_callback)
        yo_handler = CommandHandler('yo', self.bot_backend.yo_command)
        dispatcher.add_handler(yo_handler)
        insider_handler = CommandHandler('insider', self.bot_backend.insider_command)
        dispatcher.add_handler(insider_handler)
        restart_handler = CommandHandler('restart', self.bot_backend.restart_command, pass_args=True)
        dispatcher.add_handler(restart_handler)
        unknown_handler = MessageHandler(Filters.command, self.bot_backend.unknown_command)
        dispatcher.add_handler(unknown_handler)
        dispatcher.add_error_handler(self.bot_backend.error_callback)

    def start(self):
        """Start the bot server.
        """
        self.updater.start_webhook(
            listen=BOT_LISTEN_ADDRESS,
            port=BOT_WEB_HOOK_PORT,
            url_path=BOT_WEB_HOOK_URL_PATH,
            cert=BOT_CERT_PATH,
            key=BOT_KEY_PATH)
        self.updater.bot.set_webhook(url=BOT_WEB_HOOK_URL)
        logging.info('Bot: started.')

    def stop(self):
        """:#DEBUG#: Stop the bot server, often cause endless wait.
        """
        logging.info('Bot: stopping')
        self.updater.stop()
        self.stop_bot()
        logging.info('Bot: stopped.')

    def stop_bot(self):
        """Stop the queued bot."""
        self.bot.stop()
