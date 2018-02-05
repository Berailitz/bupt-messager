import logging
import threading
import time
from urllib.parse import urlsplit, parse_qs
import requests
from bs4 import BeautifulSoup
from ..config import ATTACHMENT_NAME_LENGTH, NOTICE_CHECK_INTERVAL, NOTICE_UPDATE_ERROR_SLEEP_TIME
from ..config import NOTICE_DOWNLOAD_INTERVAL, NOTICE_SUMMARY_LENGTH, NOTICE_TITLE_LENGTH
from .bot_helper import BotHelper
from .http_client import HTTPClient
from .login_helper.auth_helper import AuthHelper
from .login_helper.web_vpn_helper import WebVPNHelper

class NoticeManager(threading.Thread):
    def __init__(self, sql_handle=None, bot=None, http_client=None):
        super().__init__()
        self.http_client = http_client or HTTPClient()
        self.sql_handle = sql_handle
        self.webvpn_helper = WebVPNHelper(self.http_client)
        self.auth_helper = AuthHelper(self.http_client)
        self.bot_helper = BotHelper(self.sql_handle, bot)
        self._stop_event = threading.Event()

    def _login(self):
        self.webvpn_helper.do_login(error_notice='Web VPN (webvpn.bupt.edu.cn)')
        self.auth_helper.do_login(error_notice='Auth (my.bupt.edu.cn)')

    def run(self):
        is_first_run = True
        while is_first_run or not self._stop_event.wait(NOTICE_CHECK_INTERVAL):
            is_first_run = False
            logging.info('NoticeManager: updating.')
            self.http_client.refresh_session()
            try:
                self._login()
                self.update()
                logging.info(f'NoticeManager: Sleep for {NOTICE_CHECK_INTERVAL} seconds.')
            except KeyboardInterrupt as identifier:
                logging.warning('NoticeManager: Catch KeyboardInterrupt when logging in.')
                raise identifier
            except Exception as identifier:
                logging.exception(identifier)
                logging.error(f'NoticeManager: error when updating: {identifier}')
                logging.info(f'NoticeManager: sleep for {NOTICE_UPDATE_ERROR_SLEEP_TIME} seconds.')
                if self._stop_event.wait(NOTICE_UPDATE_ERROR_SLEEP_TIME):
                    break
        logging.info('NoticeManager: stopped.')
        self._stop_event.clear()

    def stop(self):
        self._stop_event.set()
        logging.info('NoticeManager: set stop signal.')

    def update(self):
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
    def _shape_notice(notice_dict):
        notice_dict['summary'] = notice_dict['text'][:NOTICE_SUMMARY_LENGTH]
        notice_dict['title'] = notice_dict['title'][:NOTICE_TITLE_LENGTH]
        for attachment in notice_dict['attachments']:
            attachment['name'] = attachment['name'][:ATTACHMENT_NAME_LENGTH]

    def _doanload_notice(self):
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
                logging.info(f'NoticeManager: new notice `{notice_title}`.')
            else:
                logging.info(f'NoticeManager: duplicate notice `{notice_title}`.')
        logging.info('Praser finished.')
        return notice_list
