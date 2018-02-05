import logging
from telegram.ext import Updater, CommandHandler
from ..queued_bot import queued_bot
from ..sql_handle import SQLHandle
from .backend import Backend

class BotHandle(object):
    def __init__(self, sql_manager):
        self.bot = queued_bot
        self.sql_handle = SQLHandle(sql_manager)
        self.backend = Backend(self.sql_handle)
        self.updater = Updater(bot=self.bot)

    def add_handler(self):
        dispatcher = self.updater.dispatcher
        start_handler = CommandHandler('start', self.backend.start_command)
        dispatcher.add_handler(start_handler)
        latest_handler = CommandHandler('latest', self.backend.latest_command, pass_args=True)
        dispatcher.add_handler(latest_handler)
        yo_handler = CommandHandler('yo', self.backend.latest_command)
        dispatcher.add_handler(yo_handler)

    def start(self):
        self.updater.start_polling()
        logging.info('Bot: started.')

    def stop(self):
        logging.info('Bot: stopping')
        self.updater.stop()
        logging.info('Bot: stopped.')
