import functools
import logging
import os
import sys
import telegram
from ..config import BOT_ADMIN_IDS
from ..mess import get_arg

def admin_only(func):
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        bot = get_arg(telegram.bot, args, kwargs)
        update = get_arg(telegram.update, args, kwargs)
        user_id = update.effective_user.id
        if user_id not in BOT_ADMIN_IDS:
            logging.warning(f"BotBackend: Unauthorized attempt to `{func.__name__}` from `{user_id}`.")
            bot.send_message(chat_id=update.message.chat_id, text="Didn't understand...")
            return
        return func(*args, **kwargs)
    return wrapped

def restart_app(updater):
    """Gracefully stop the Updater and replace the current process with a new one"""
    updater.stop()
    os.execl(sys.executable, sys.executable, *sys.argv)
