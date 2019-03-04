"""Notification spider."""
import datetime
import functools
import logging
import json
import threading
import time
from queue import Queue
from typing import List
from bs4 import BeautifulSoup
from ..config import ATTACHMENT_NAME_LENGTH, BROADCAST_CYCLE, NOTICE_CHECK_INTERVAL, NOTICE_UPDATE_ERROR_SLEEP_TIME
from ..config import NOTICE_DOWNLOAD_INTERVAL, NOTICE_SUMMARY_LENGTH, NOTICE_TITLE_LENGTH, NOTICE_AUTHOR_LENGTH
from ..config import STATUS_ERROR_DOWNLOAD, STATUS_SYNCED, PAGE_COUNTER_PER_UPDATE
from ..mess import fun_logger
from ..sql_handler import SQLHandler
from .bot_helper import BotHelper
from .http_client import HTTPClient


def change_status(*, error_status: int = None, ok_status: int = None):
    """Decorated functions will insert `ok_status` or `error_status` into table `status`,
    if any error occured.

    :param error_status: Error status code, defaults to None and not log will be inserted.
    :type error_status: int, optional.
    :param ok_status: Status code for success, defaults to None and not log will be inserted.
    :type ok_status: int, optional.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            self = args[0]
            try:
                result = func(*args, **kw)
            except Exception as identifier:
                if error_status is not None:
                    self.sql_handler.insert_status(error_status)
                raise identifier
            else:
                if ok_status is not None:
                    self.sql_handler.insert_status(ok_status)
            return result
        return wrapper
    return decorator


class NoticeManager(threading.Thread):
    """Fetch notices from `my.bupt.edu.cn`.

    :member _stop_event: :obj:`threading.Event` to stop manager.
    """
    def __init__(self, sql_handler=None, bot=None, http_client=None):
        super().__init__()
        self.http_client = http_client or HTTPClient()
        self.sql_handler = sql_handler
        self.bot_helper = BotHelper(self.sql_handler, bot)
        self._stop_event = threading.Event()

    def run(self):
        """Main loop.
        """
        is_first_run = True
        update_counter = 0
        while is_first_run or not self._stop_event.wait(NOTICE_CHECK_INTERVAL):
            update_counter += 1
            is_first_run = False
            logging.info(f'NoticeManager: Updating. ({update_counter} / {BROADCAST_CYCLE})')
            self.http_client.refresh_session()
            try:
                notice_dict_list = self._doanload_notice()
                self.update(notice_dict_list)
                if update_counter >= BROADCAST_CYCLE:
                    update_counter = 0
                    for new_notice in self.sql_handler.get_unpushed_notices():
                        self.bot_helper.broadcast_notice(new_notice)
                        self.sql_handler.mark_pushed(new_notice.id)
                logging.info(f'NoticeManager: Sleep for {NOTICE_CHECK_INTERVAL} seconds.')
            except KeyboardInterrupt as identifier:
                logging.warning('NoticeManager: Catch KeyboardInterrupt when logging in.')
                raise identifier
            except Exception as identifier:
                logging.exception(identifier)
                logging.error(f'NoticeManager: Error occured when updating: {identifier}')
                logging.info(f'NoticeManager: Sleep for {NOTICE_UPDATE_ERROR_SLEEP_TIME} seconds.')
                if self._stop_event.wait(NOTICE_UPDATE_ERROR_SLEEP_TIME):
                    break
        logging.info('NoticeManager: Stopped.')
        self._stop_event.clear()

    def stop(self):
        """Stop manager thread by setting :attr:`_stop_event`.
        """
        self._stop_event.set()
        logging.info('NoticeManager: Set stop signal.')

    @change_status(ok_status=STATUS_SYNCED)
    def update(self, notice_dict_list) -> int:
        """Fetch new notice.

        :return: Amount of new notice.
        :rtype: int.
        """
        notice_counter = 0
        for notice_dict in notice_dict_list:
            self.sql_handler.insert_notice(notice_dict)
            notice_counter += 1
        logging.info(f'{notice_counter} notifications inserted.')
        return notice_counter

    def get_attachments(self, notice_id: str):
        """Fetch attachment info.

        :return: List of attachment dicts.
        :rtype: list.
        """
        detail_soup = BeautifulSoup(
            self.http_client.get(
                f'https://webapp.bupt.edu.cn/extensions/wap/news/detail.html?id={notice_id}&classify_id=tzgg'
            ).text, 'lxml')
        return [{
            'name': attachement_label.text[:ATTACHMENT_NAME_LENGTH],
            'notice_id': notice_id,
            'url': attachement_label['href']
        } for attachement_label in detail_soup.select(
            '#container > section > ul > div > p > a')]

    def prase_notice(self, notice_raw: dict):
        """Form a notice dict, without attachment. Generate summary, cut title and link attachments.

        :param notice_dict: New notification.
        :type notice_dict: dict.
        """
        notice_dict = dict()
        notice_dict['author'] = notice_raw['author'][:NOTICE_AUTHOR_LENGTH]
        notice_dict['id'] = notice_raw['id']
        notice_dict['html'] = notice_raw['text'].replace('&nbsp;', '')
        notice_dict['summary'] = notice_raw['desc'].replace('&nbsp;', '')[:NOTICE_SUMMARY_LENGTH]
        notice_dict['time'] = datetime.datetime.fromtimestamp(int(notice_raw['created']))
        notice_dict['title'] = notice_raw['title'].replace('&nbsp;', '')[:NOTICE_TITLE_LENGTH]
        notice_dict['url'] = f'https://webapp.bupt.edu.cn/extensions/wap/news/detail.html?id={notice_raw["id"]}&classify_id=tzgg'
        return notice_dict

    def download_notice_list_page(self, page_index=1):
        """Download a list of notice dicts.

        :return: List of notice dicts or None.
        :rtype: list.
        """
        try:
            logging.info(f'NoticeManager: Download notice list at page `{page_index}`.')
            notice_response = self.http_client.get(
                f'https://webapp.bupt.edu.cn/extensions/wap/news/get-list.html?p={page_index}&type=tzgg'
            )
            notice_data = json.loads(notice_response.text)
            if notice_data['m'] == '操作成功':
                return [
                    notice for notice_list in notice_data['data'].values()
                    for notice in notice_list
                ]
        except Exception as identifier:
            logging.exception(identifier)
            logging.warning(f'NoticeManager: Failed to download notice list.')
            return None

    @change_status(error_status=STATUS_ERROR_DOWNLOAD)
    @fun_logger(log_fun=logging.debug)
    def _doanload_notice(self) -> List[dict]:
        """Download new notices.

        :rtype: List[dict].
        """
        notice_list = list()
        for page_index in range(PAGE_COUNTER_PER_UPDATE):
            notice_raw_list = self.download_notice_list_page(page_index + 1)
            logging.info(f'{len(notice_raw_list)} notice detected.')
            for notice_raw in notice_raw_list:
                notice_dict = self.prase_notice(notice_raw)
                if self.sql_handler.is_new_notice(notice_dict['id']):
                    logging.info(f"NoticeManager: Waiting for attachment of `{notice_dict['title']}`.")
                    time.sleep(NOTICE_DOWNLOAD_INTERVAL)
                    notice_dict['attachments'] = self.get_attachments(notice_dict['id'])
                    notice_list.append(notice_dict)
                    logging.info(f'NoticeManager: New notice fetched `{notice_dict["title"]}`.')
                else:
                    logging.info(f'NoticeManager: Duplicate notice `{notice_dict["title"]}`.')
            else:
                break
        logging.info('NoticeManager: Download finished.')
        return notice_list

def create_notice_manager(sql_manager, bot):
    """Create a `NoticeManager`.

    :param sql_manager: Manager `session`s.
    :type sql_manager: SQLManager.
    :return: New :obj:`NoticeManager`.
    :rtype: NoticeManager.
    """
    sql_handler = SQLHandler(sql_manager)
    notice_manager = NoticeManager(sql_handler=sql_handler, bot=bot)
    return notice_manager
