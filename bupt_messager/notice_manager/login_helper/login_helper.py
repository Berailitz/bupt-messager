import logging
import time
from bs4 import BeautifulSoup

class LoginHelper(object):
    def __init__(self, http_client=None):
        self.max_attempt = 10
        self.wait_intervel = 5
        self.http_client = http_client

    def init_http_client(self, http_client):
        self.http_client = http_client

    def _login(self):
        pass

    def response_checker(self, login_response):
        """Check response from login action, return error description(True)
        for error or None(False) for success."""
        return None

    def try_login(self):
        is_first_time = True
        for login_counter in range(self.max_attempt):
            is_first_time = False
            try:
                login_response = self._login()
                login_result = self.response_checker(login_response)
                if not login_result:
                    logging.info(f'Login result: Success.')
                    return login_response
                else:
                    logging.warning(f'{login_counter}th login result: `{login_result}`')
                    logging.info(f'Wait for next attempt. ({login_counter} / {self.max_attempt})')
            except KeyboardInterrupt as identifier:
                logging.warning('Catch KeyboardInterrupt when logging in.')
                raise identifier
            except Exception as identifier:
                logging.exception(identifier)
                logging.error('Error occered when trying to login.')
            finally:
                time.sleep(self.wait_intervel)
        return False

    def do_login(self, error_notice=None):
        if not self.try_login():
            raise PermissionError(f'Cannot login: `{error_notice}`.')
