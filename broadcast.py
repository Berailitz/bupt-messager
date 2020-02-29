import argparse
import time
import logging
from pathlib import Path
from telegram import ParseMode
from bupt_messager.bupt_messager import BUPTMessager
from bupt_messager.mess import set_logger



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("text", type=str, help='Text to broadcast.')
    parser.add_argument("--chat-ids", type=int, help='ID of chats to broadcast, all chats by default.', nargs='+', default=[])
    args = parser.parse_args()
    messager = BUPTMessager(no_bot_mode=True, no_spider_mode=True)
    text = args.text
    if len(args.chat_ids) > 0:
        chat_ids = args.chat_ids
    else:
        chat_ids = messager.notice_manager.bot_helper.sql_handler.get_chat_ids()
    bot = messager.notice_manager.bot_helper.bot
    logging.warning(f'Broadcast to {len(chat_ids)} subscribers: `{text}`.')
    for chat_id in chat_ids:
        bot.send_message(chat_id=chat_id, text=text, parse_mode=ParseMode.MARKDOWN)
    messager.stop()


if __name__ == "__main__":
    main()
