import logging
from telegram.ext import Filters, Updater, CallbackQueryHandler, CommandHandler, MessageHandler
from ..config import WEB_HOOK_PORT, WEB_HOOK_URL, WEB_HOOK_URL_PATH
from ..sql_handle import SQLHandle
from .bot_backend import BotBackend

class BotHandler(object):
    def __init__(self, sql_manager=None, bot=None):
        self.updater = Updater(bot=bot) if bot else None
        self.bot_backend = BotBackend(
            sql_handle=SQLHandle(sql_manager=sql_manager),
            updater=self.updater
        )

    def init_bot_backend(self, sql_manager):
        self.bot_backend.sql_handle.init_sql_manager(sql_manager)

    def init_updater(self, bot):
        self.updater = Updater(bot=bot)

    def add_handler(self):
        dispatcher = self.updater.dispatcher
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
        restart_handler = CommandHandler('restart', self.bot_backend.restart_command, pass_args=True)
        dispatcher.add_handler(restart_handler)
        unknown_handler = MessageHandler(Filters.command, self.bot_backend.unknown_command)
        dispatcher.add_handler(unknown_handler)

    def start(self):
        self.updater.start_webhook(port=WEB_HOOK_PORT, url_path=WEB_HOOK_URL_PATH)
        self.updater.bot.set_webhook(url=WEB_HOOK_URL)
        logging.info('Bot: started.')

    def stop(self):
        logging.info('Bot: stopping')
        self.updater.stop()
        logging.info('Bot: stopped.')
