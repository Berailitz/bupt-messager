"""Notification spider."""
import functools
import logging
import threading
import time
from typing import List
from urllib.parse import urlsplit, parse_qs
from bs4 import BeautifulSoup
from ..config import ATTACHMENT_NAME_LENGTH, NOTICE_CHECK_INTERVAL, NOTICE_UPDATE_ERROR_SLEEP_TIME
from ..config import NOTICE_DOWNLOAD_INTERVAL, NOTICE_SUMMARY_LENGTH, NOTICE_TITLE_LENGTH
from ..config import STATUS_ERROR_DOWNLOAD, STATUS_ERROR_LOGIN_AUTH, STATUS_ERROR_LOGIN_WEBVPN, STATUS_SYNCED
from ..sql_handle import SQLHandle
from .bot_helper import BotHelper
from .http_client import HTTPClient
from .login_helper.auth_helper import AuthHelper
from .login_helper.web_vpn_helper import WebVPNHelper


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
                    self.sql_handle.insert_status(error_status)
                raise identifier
            else:
                if ok_status is not None:
                    self.sql_handle.insert_status(ok_status)
            return result
        return wrapper
    return decorator


class NoticeManager(threading.Thread):
    """Fetch notices from `my.bupt.edu.cn`.

    :member _stop_event: :obj:`threading.Event` to stop manager.
    """
    def __init__(self, sql_handle=None, bot=None, http_client=None):
        super().__init__()
        self.http_client = http_client or HTTPClient()
        self.sql_handle = sql_handle
        self.webvpn_helper = WebVPNHelper(self.http_client)
        self.auth_helper = AuthHelper(self.http_client)
        self.bot_helper = BotHelper(self.sql_handle, bot)
        self._stop_event = threading.Event()

    @change_status(error_status=STATUS_ERROR_LOGIN_WEBVPN)
    def _login_webvpn(self):
        """Log in to web VPN.
        """
        self.webvpn_helper.do_login(error_notice='Web VPN (webvpn.bupt.edu.cn)')

    @change_status(error_status=STATUS_ERROR_LOGIN_AUTH)
    def _login_auth(self):
        """Log in to `my.bupt.edu.cn`.
        """
        self.auth_helper.do_login(error_notice='Auth (my.bupt.edu.cn)')

    def run(self):
        """Main loop.
        """
        is_first_run = True
        while is_first_run or not self._stop_event.wait(NOTICE_CHECK_INTERVAL):
            is_first_run = False
            logging.info('NoticeManager: Updating.')
            self.http_client.refresh_session()
            try:
                self._login_webvpn()
                self._login_auth()
                self.update()
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
    def update(self) -> int:
        """Fetch new notice.

        :return: Amount of new notice.
        :rtype: int.
        """
        update_counter = 0
        notice_list = self._doanload_notice()
        for notice_dict in notice_list:
            self._shape_notice(notice_dict)
            self.sql_handle.insert_notice(notice_dict)
            self.bot_helper.broadcast_notice(notice_dict)
            update_counter += 1
        logging.info(f'{update_counter} notifications inserted.')
        return update_counter

    @staticmethod
    def _shape_notice(notice_dict: dict):
        """Format a notice. Generate summary, cut title and link attachments.

        :param notice_dict: New notification.
        :type notice_dict: dict.
        """
        notice_dict['summary'] = notice_dict['text'][:NOTICE_SUMMARY_LENGTH]
        notice_dict['title'] = notice_dict['title'][:NOTICE_TITLE_LENGTH]
        for attachment in notice_dict['attachments']:
            attachment['name'] = attachment['name'][:ATTACHMENT_NAME_LENGTH]

    @change_status(error_status=STATUS_ERROR_DOWNLOAD)
    def _doanload_notice(self) -> List[dict]:
        """Download new notices.

        :rtype: List[dict].
        """
        NOTICE_LIST_URL = 'http://my.bupt.edu.cn/detach.portal?.pen=pe1144&.pmn=view%27'
        NOTICE_BASEURL = 'http://my.bupt.edu.cn/'
        LINK_DIV_SELECTOR = '#fpe1144 > ul > li'
        notice_list = list()
        notice_index_soup = BeautifulSoup(self.http_client.get(NOTICE_LIST_URL).text, 'lxml')
        logging.info(f'Prasing `{notice_index_soup.title.text}`')
        notice_item_list = notice_index_soup.select(LINK_DIV_SELECTOR)
        logging.info(f'{len(notice_item_list)} links detected.')
        for notice_item in notice_item_list:
            notice_link = notice_item.select('a')[0]
            notice_url = NOTICE_BASEURL + notice_link['href']
            notice_id = parse_qs(urlsplit(notice_url).query)['bulletinId'][0]
            notice_title = notice_link.text
            if self.sql_handle.is_new_notice(notice_id):
                notice_info = dict()
                notice_info['url'] = notice_url
                notice_info['id'] = notice_id
                notice_info['title'] = notice_title
                notice_info['date'] = notice_item.select('span.time')[0].text
                logging.info(f"Waiting for `{notice_info['title']}`.")
                time.sleep(NOTICE_DOWNLOAD_INTERVAL)
                notice_page_soup = BeautifulSoup(self.http_client.get(notice_info['url']).text, 'lxml')
                notice_info['text'] = notice_page_soup.select('.singleinfo')[0].text
                notice_attachment = notice_page_soup.select('.battch')
                if notice_attachment:
                    notice_info['attachments'] = [
                        {'name': item.text, 'url': NOTICE_BASEURL + item['href']} for item in notice_attachment[0].select('a')
                    ]
                else:
                    notice_info['attachments'] = []
                notice_list.append(notice_info)
                logging.info(f'NoticeManager: New notice `{notice_title}`.')
            else:
                logging.info(f'NoticeManager: Duplicate notice `{notice_title}`.')
        logging.info('NoticeManager: Praser finished.')
        return notice_list

def create_notice_manager(sql_manager, bot):
    """Create a `NoticeManager`.

    :param sql_manager: Manager `session`s.
    :type sql_manager: SQLManager.
    :return: New :obj:`NoticeManager`.
    :rtype: NoticeManager.
    """
    sql_handle = SQLHandle(sql_manager)
    notice_manager = NoticeManager(sql_handle=sql_handle, bot=bot)
    return notice_manager
