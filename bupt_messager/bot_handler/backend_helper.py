import functools
import logging
import os
import sys
import telegram
from telegram import ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from ..config import BOT_ADMIN_IDS, BOT_NOTICE_MAX_BUTTON_PER_LINE
from ..mess import get_arg, threaded

def admin_only(func):
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
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
    def __init__(self, *, sql_handle=None, updater=None):
        self.sql_handle = sql_handle
        self.updater = updater

    def init_sql_handle(self, sql_handle):
        self.sql_handle = sql_handle

    def init_updater(self, updater):
        self.updater = updater

    @threaded
    def restart_app(self):
        """Gracefully stop the Updater and replace the current process with a new one"""
        self.updater.stop()
        os.execl(sys.executable, sys.executable, *sys.argv)

    @staticmethod
    def markup_keyboard(buttons, width, header_buttons=None, footer_buttons=None):
        menu = [buttons[i:i + width] for i in range(0, len(buttons), width)]
        if header_buttons:
            menu.insert(0, header_buttons)
        if footer_buttons:
            menu.append(footer_buttons)
        return InlineKeyboardMarkup(menu)

    def send_latest_notice(self, *, bot, message, length, start=0):
        text = ""
        buttons = []
        for index, notice in enumerate(self.sql_handle.get_latest_notices(length=length, start=start)):
            text += f'{index + 1}.[{notice.title}]({notice.url})({notice.date})\n'
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
    def prase_callback(update):
        return update.callback_query.data.split('_')[1:]
