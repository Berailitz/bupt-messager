import logging
import telegram.bot
from telegram.ext import messagequeue
from .config import BOT_ALL_BURST_LIMIT, BOT_GROUP_BURST_LIMIT, BOT_TOKEN, PROXY_URL

class QueuedBot(telegram.bot.Bot):
    '''A subclass of Bot which delegates send method handling to MQ'''
    def __init__(self, msg_queue, *args, is_queued_def=True, **kwargs):
        super().__init__(*args, **kwargs)
        # below 2 attributes should be provided for decorator usage
        self._is_messages_queued_default = is_queued_def
        self._msg_queue = msg_queue

    def __del__(self):
        try:
            self._msg_queue.stop()
        except KeyboardInterrupt as identifier:
            logging.warning('QueuedBot: Catch KeyboardInterrupt when stopping message queue.')
            raise identifier
        except Exception as identifier:
            logging.error('QueuedBot: Error occured when stopping message queue.')
            logging.exception(identifier)

    @messagequeue.queuedmessage
    def send_message(self, *args, **kwargs):
        '''Wrapped method would accept new `queued` and `isgroup`
        OPTIONAL arguments'''
        return super().send_message(*args, **kwargs)

def create_queued_bot():
    msg_queue = messagequeue.MessageQueue(all_burst_limit=BOT_ALL_BURST_LIMIT, group_burst_limit=BOT_GROUP_BURST_LIMIT)
    _my_request = telegram.utils.request.Request(proxy_url=PROXY_URL)
    queued_bot = QueuedBot(msg_queue, token=BOT_TOKEN, request=_my_request)
    return queued_bot
