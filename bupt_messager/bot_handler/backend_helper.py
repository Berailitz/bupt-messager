"""Utils for backend."""
import functools
import logging
import os
import sys
from typing import List
import telegram
from telegram import ParseMode, InlineKeyboardButton, InlineKeyboardMarkup, Update
from ..config import BOT_ADMIN_IDS, BOT_NOTICE_MAX_BUTTON_PER_LINE, BOT_RESTART_ARG_NO_ARG, BOT_START_VALID_ARGS
from ..mess import fun_logger, get_arg, threaded


def admin_only(func):
    """Decorated function will be restricted to admins listed in `BOT_ADMIN_IDS` only.
    """
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        """See `admin_only`.
        """
        bot = get_arg(telegram.bot.Bot, args, kwargs)
        update = get_arg(telegram.update.Update, args, kwargs)
        user_id = update.effective_user.id
        if user_id not in BOT_ADMIN_IDS:
            logging.warning(f"BotBackend: Unauthorized attempt to `{func.__name__}` from `{user_id}`.")
            bot.send_message(chat_id=update.message.chat_id, text="Didn't understand...")
            return
        return func(*args, **kwargs)
    return wrapped


class BackendHelper(object):
    """Tools for `BotBackend`.

    :member sql_handler: Attached :obj: SQLHandler.
    :type sql_handler: SQLHandler.
    :member updater: Attached :obj: bot updater.
    :type updater: Updater.
    """
    def __init__(self, *, sql_handler=None, updater=None):
        self.sql_handler = sql_handler
        self.updater = updater

    def init_sql_handle(self, sql_handler):
        self.sql_handler = sql_handler

    def init_updater(self, updater):
        self.updater = updater

    @threaded
    def restart_app(self, args: List[str]):
        """Gracefully kill current process and replace it with a new one.

        :param args: List of restart arguments (str) received from client.
        :type args: list.
        """
        start_commands = ['--' + arg for arg in args if arg in BOT_START_VALID_ARGS]
        self.updater.stop()
        if BOT_RESTART_ARG_NO_ARG in args:
            os.execl(sys.executable, sys.executable, sys.argv[0])
        elif start_commands:
            os.execl(sys.executable, sys.executable, sys.argv[0], *start_commands)
        else:
            os.execl(sys.executable, sys.executable, *sys.argv)

    @staticmethod
    def markup_keyboard(buttons: List[InlineKeyboardButton],
                        width: int,
                        header_buttons: List[InlineKeyboardButton] = None,
                        footer_buttons: List[InlineKeyboardButton] = None) -> InlineKeyboardMarkup:
        """Build keybords from buttons.

        :param buttons: Buttons displayed in the middle.
        :type buttons: List[InlineKeyboardButton].
        :param width: Amount of buttons per line.
        :type width: int.
        :param header_buttons: Defaults to None. Buttons on the first line.
        :type header_buttons: List[InlineKeyboardButton], optional.
        :param footer_buttons: Defaults to None. Buttons on the last line.
        :type footer_buttons: List[InlineKeyboardButton], optional.
        :return: Keyboard in :obj:`InlineKeyboardMarkup`.
        :rtype: InlineKeyboardMarkup.
        """
        menu = [buttons[i:i + width] for i in range(0, len(buttons), width)]
        if header_buttons:
            menu.insert(0, header_buttons)
        if footer_buttons:
            menu.append(footer_buttons)
        return InlineKeyboardMarkup(menu)

    def send_notice(self, bot, message: telegram.Message, index: int):
        """Send a notice to a specific user.

        :param bot: Current bot.
        :type bot: telegram.bot.
        :param message: Request received.
        :type message: telegram.Message.
        :param index: Index of the message to be sent.
        :type index: int.
        """
        notice_list = self.sql_handler.get_latest_notices(length=1, start=index)
        if notice_list:
            target_notice = notice_list[0]
            keyboard = [[InlineKeyboardButton('READ', target_notice.url)]]
            menu_markup = InlineKeyboardMarkup(keyboard)
            bot.send_message(
                chat_id=message.chat_id,
                text=f"*{target_notice.title}*\n{target_notice.summary}...({target_notice.datetime})",
                reply_markup=menu_markup,
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            bot.send_message(chat_id=message.chat_id, text="No such notice.")

    def send_latest_notice(self, *, bot, message: telegram.Message, length: int, start: int = 0):
        """Send a list of notices.

        :param message: Message received.
        :type message: telegram.Message.
        :param length: Amount to notices to be sent.
        :type length: int.
        :param start: Defaults to 0. Index of the most recent notice to be sent.
        :type start: int, optional.
        """
        text = ""
        buttons = []
        for index, notice in enumerate(self.sql_handler.get_latest_notices(length=length, start=start)):
            text += f'{index + 1}.[{notice.title}]({notice.url})({notice.datetime})\n'
            buttons.append(InlineKeyboardButton(text=f'{index + 1}', callback_data=f'read_{start + index}'))
        keyboard = self.markup_keyboard(
            buttons=buttons,
            width=BOT_NOTICE_MAX_BUTTON_PER_LINE,
            footer_buttons=[InlineKeyboardButton(text='more', callback_data=f'latest_{length}_{start + length}')]
        )
        if text:
            bot.send_message(
                chat_id=message.chat_id,
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboard)
        else:
            bot.send_message(chat_id=message.chat_id, text='No more news.')

    @staticmethod
    @fun_logger(log_fun=logging.debug)
    def prase_callback(update: Update) -> List[str]:
        """Prase callback arguments from argument `args` received from `updater`.

        :param update: Callback update.
        :type update: telegram.Update.
        :return: List of arguments.
        :rtype: List[str].
        """
        return update.callback_query.data.split('_')[1:]
