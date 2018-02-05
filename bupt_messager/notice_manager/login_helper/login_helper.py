import logging
import time
from ...config import LOGIN_MAX_ATTEMPT, LOGIN_WAIT_INTERVEL

class LoginHelper(object):
    def __init__(self, http_client=None):
        self.max_attempt = LOGIN_MAX_ATTEMPT
        self.wait_intervel = LOGIN_WAIT_INTERVEL
        self.http_client = http_client

    def init_http_client(self, http_client):
        self.http_client = http_client

    def _login(self):
        raise NotImplementedError

    def response_checker(self, login_response):
        """Check response from login action, return error description(True)
        for error or None(False) for success."""
        logging.warning('LoginHelper: `response_checker` NOT implemented.')
        return None

    def do_login(self, error_notice=None):
        for login_counter in range(self.max_attempt):
            try:
                login_response = self._login()
                login_result = self.response_checker(login_response)
                if not login_result:
                    logging.info(f'LoginHelper: result: success.')
                    return login_response
                else:
                    logging.warning(f'LoginHelper: error `{login_result}`. ({login_counter} / {self.max_attempt})')
            except KeyboardInterrupt as identifier:
                logging.warning('LoginHelper: Catch KeyboardInterrupt when logging in.')
                raise identifier
            except Exception as identifier:
                logging.error(f'LoginHelper: Unexcepted error occered when logging in: {identifier}')
                if login_counter == self.max_attempt - 1:
                    logging.error(f'LoginHelper: Cannot login: `{error_notice}`.')
                    raise identifier
            finally:
                time.sleep(self.wait_intervel)

    def try_login(self, error_notice=None):
        try:
            return self.try_login(error_notice=error_notice)
        except Exception:
            return False
