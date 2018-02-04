import logging
import time
from bs4 import BeautifulSoup

class LoginHelper(object):
    def __init__(self, http_client=None):
        self.max_attempt = 10
        self.wait_intervel = 5
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
                    logging.info(f'Auth login result: Success.')
                    return login_response
                else:
                    logging.info(f'{login_counter}th login result: `{login_result}`')
                    logging.info(f'Wait for next attempt.')
            except KeyboardInterrupt as identifier:
                logging.warning('Catch KeyboardInterrupt when logging in.')
                raise identifier
            except Exception as identifier:
                logging.exception(identifier)
                logging.error('Error occered when trying to login.')
            finally:
                time.sleep(self.wait_intervel)
        return False

    def do_login(self, http_client=None, error_notice=None, max_attempt=None):
        self.max_attempt = max_attempt or self.max_attempt
        try:
            self.http_client = http_client or self.http_client
        except AttributeError as attr_error:
            raise ValueError(f'No `success_title` or `http_client` specified: {attr_error.args}')
        if not self.try_login():
            raise PermissionError(f'Cannot login: {error_notice}')
