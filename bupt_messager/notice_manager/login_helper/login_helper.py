import logging
import time
from bs4 import BeautifulSoup

class LoginHelper(object):
    def __init__(self, http_client=None, soup_checker=None):
        self.max_attempt = 10
        self.wait_intervel = 5
        self.soup_checker = soup_checker
        self.http_client = http_client

    def _login(self):
        pass

    def try_login(self):
        is_first_time = True
        for login_counter in range(self.max_attempt):
            is_first_time = False
            login_response = self._login()
            login_result_soup = BeautifulSoup(login_response.text, 'lxml')
            if self.soup_checker and self.soup_checker(login_result_soup):
                logging.info(f'Auth login result: Success.')
                return login_result_soup
            else:
                logging.info(f'{login_counter}th login result: `{login_result_soup.title.text}`')
                logging.info(f'Wait for next attempt.')
                time.sleep(self.wait_intervel)
        return False

    def do_login(self, http_client=None, soup_checker=None, error_notice=None, max_attempt=None):
        self.max_attempt = max_attempt or self.max_attempt
        try:
            self.http_client = http_client or self.http_client
            self.soup_checker = soup_checker or self.soup_checker
        except AttributeError as attr_error:
            raise ValueError(f'No `success_title` or `http_client` specified: {attr_error.args}')
        if not self.try_login():
            raise PermissionError(f'Cannot login: {error_notice}')
