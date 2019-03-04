import time
from bupt_messager.bupt_messager import BUPTMessager
b=BUPTMessager()

class A():pass

a=A()


l=b.notice_manager.bot_helper.sql_handler.get_chat_ids()

bot = b.notice_manager.bot_helper.bot

for ll in l:
    bot.send_message(chat_id=ll, text="Oops, 抱歉bot抽风了一下，刚刚推送的是之前的通知，剩余的几篇明天推...")
    time.sleep(2)


252320854
bot.send_message(chat_id=252320854, text="Oops, 抱歉bot抽风了一下，刚刚推送的是之前的通知，剩余的几篇明天推")
