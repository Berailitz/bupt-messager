"""Telegram bot with message queue."""
import logging
import traceback
from typing import Callable
import telegram.bot
from telegram import ParseMode
from telegram.ext import messagequeue
from .config import BOT_ADMIN_IDS, BOT_ALL_BURST_LIMIT, BOT_GROUP_BURST_LIMIT, BOT_TOKEN, PROXY_URL


class QueuedBot(telegram.bot.Bot):
    """A bot which delegates send method handling to message queues.

    :member _is_messages_queued_default: Whether messages are queued by default.
    :member _msg_queue: Queue for messages.
    :type _msg_queue: MessageQueue.
    """
    def __init__(self, msg_queue, *args, is_queued_def=True, error_handle: Callable = None, **kwargs):
        """Initialize bot and attach `msg_queue` to bot.

        :param msg_queue: Queue for messages.
        :type msg_queue: MessageQueue.
        :param *args: Arguments to initialize bot.
        :type *args: list.
        :param **kwargs: keyword arguments.
        :type **kwargs: dict.
        :param is_queued_def: Whether messages are queued by default, defaults to True.
        :type is_queued_def: bool, option.
        """
        super().__init__(*args, **kwargs)
        self._is_messages_queued_default = is_queued_def
        self._msg_queue = msg_queue
        self.error_handle = error_handle

    def set_error_handle(self, error_handle: Callable):
        self.error_handle = error_handle

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
    def send_message(self, *args, **kwargs) -> telegram.Message:
        """Send message by pushing messages to message queue,
        and accept new `queued` and `isgroup` keyword arguments.
        """
        try:
            return super().send_message(*args, **kwargs)
        except Exception as identifier:
            if self.error_handle is not None:
                if 'chat_id' in kwargs.keys():
                    chat_id = kwargs['chat_id']
                else:
                    chat_id = args[0]
                self.error_handle(identifier, chat_id=chat_id)
            else:
                raise identifier

    def send_error_report(self):
        """Send error report to all admins.

        :param bot: Current bot.
        :type bot: telegram.bot.
        :param notice: Notification to be sent.
        :param index: Index of the message to be sent.
        """
        error_text = f'```\n{traceback.format_exc()}```'
        for admin_chat_id in BOT_ADMIN_IDS:
            self.send_message(
                chat_id=admin_chat_id,
                text=error_text,
                parse_mode=ParseMode.MARKDOWN)

    def stop(self):
        """Stop the message queue."""
        self._msg_queue.stop()


def create_queued_bot():
    """Factorial function to create queued bot.
    """
    msg_queue = messagequeue.MessageQueue(all_burst_limit=BOT_ALL_BURST_LIMIT, group_burst_limit=BOT_GROUP_BURST_LIMIT)
    _my_request = telegram.utils.request.Request(proxy_url=PROXY_URL)
    queued_bot = QueuedBot(msg_queue, token=BOT_TOKEN, request=_my_request)
    return queued_bot
