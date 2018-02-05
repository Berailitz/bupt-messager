import logging
from telegram.ext import Updater, CommandHandler
from ..sql_handle import SQLHandle
from .bot_backend import BotBackend

class BotHandle(object):
    def __init__(self, sql_manager=None, bot=None):
        self.bot_backend = BotBackend(sql_handle=SQLHandle(sql_manager=sql_manager))
        self.updater = Updater(bot=bot) if bot else None

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
        yo_handler = CommandHandler('yo', self.bot_backend.yo_command)
        dispatcher.add_handler(yo_handler)

    def start(self):
        self.updater.start_webhook(port=9051, url_path='bupt_messager')
        self.updater.bot.set_webhook(webhook_url='https://bot.ohhere.xyz/bupt_messager')
        logging.info('Bot: started.')

    def stop(self):
        logging.info('Bot: stopping')
        self.updater.stop()
        logging.info('Bot: stopped.')
