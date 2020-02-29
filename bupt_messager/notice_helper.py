from telegram import ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from .config import NOTICE_TEXT, NOTICE_MESSAGE_SUMMARY_LENGTH
from .models import Notification


def send_notice(bot, chat_id: int, notice: Notification = None):
    """Send a notice to a specific user.

    :param bot: Current bot.
    :type bot: telegram.bot.
    :param notice: Notification to be sent.
    :param index: Index of the message to be sent.
    """
    keyboard = [[InlineKeyboardButton('READ', notice.url)]]
    if notice.attachments:
        keyboard += [
            [InlineKeyboardButton(attachment.name, attachment.url)]
            for attachment in notice.attachments
        ]
    menu_markup = InlineKeyboardMarkup(keyboard)
    bot.send_message(
        chat_id=chat_id,
        text=NOTICE_TEXT.format(
            title=notice.title,
            summary=notice.summary[:NOTICE_MESSAGE_SUMMARY_LENGTH],
            datetime=notice.datetime,
            id=notice.id),
        reply_markup=menu_markup,
        parse_mode=ParseMode.MARKDOWN)
