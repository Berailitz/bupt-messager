"""Login helper logic."""
import logging
import time
from ...config import LOGIN_MAX_ATTEMPT, LOGIN_WAIT_INTERVEL


class LoginHelper(object):
    """Base class for login.
    """
    def __init__(self, http_client=None):
        self.max_attempt = LOGIN_MAX_ATTEMPT
        self.wait_intervel = LOGIN_WAIT_INTERVEL
        self.http_client = http_client

    def init_http_client(self, http_client):
        self.http_client = http_client

    def _login(self):
        """Send login requests.

        :raises NotImplementedError: If this method is not impemented.
        """
        raise NotImplementedError

    def response_checker(self, login_response):
        """Check response from login action, return error description(True)
        for error or `None` for success.

        :param login_response: Response of login request.
        :type login_response: Requests.Response.
        :return: Error message if error occured.
        :rtype: str|None.
        """
        logging.warning('LoginHelper: `response_checker` NOT implemented.')
        return None

    def do_login(self, error_notice=None):
        """Send login requests for :attr:`max_attempt` times, raise last error if failed.

        :param error_notice: Notice to show if failed to log in, defaults to None.
        :type error_notice: str, optional.
        :raises identifier: Error occured.
        :raises PermissionError: Login fails due to unknown error.
        :return: Login response.
        :rtype: requests.Response.
        """
        for login_counter in range(self.max_attempt):
            try:
                login_response = self._login()
                login_result = self.response_checker(login_response)
                if not login_result:
                    logging.info(f'LoginHelper: Result: Success.')
                    return login_response
                else:
                    logging.warning(f'LoginHelper: ({login_counter + 1} / {self.max_attempt}) Error `{login_result}`.')
            except KeyboardInterrupt as identifier:
                logging.warning('LoginHelper: Catch KeyboardInterrupt when logging in.')
                raise identifier
            except Exception as identifier:
                logging.error(f'LoginHelper: ({login_counter + 1} / {self.max_attempt}) Error when logging in: {identifier}')
                if login_counter == self.max_attempt - 1:
                    logging.error(f'LoginHelper: Cannot login: `{error_notice}`.')
                    raise identifier
            finally:
                time.sleep(self.wait_intervel)
        raise PermissionError(f'LoginHelper: Cannot login: `{error_notice}`.')

    def try_login(self, error_notice=None):
        """Try to log in, return response if succeeded, or False if failed.

        :param error_notice: Notice to show if failed to log in, defaults to None.
        :type error_notice: str, optional.
        :raises KeyboardInterrupt: Keyboard interruption.
        :return: Login response.
        :rtype: requests.Response|None.
        """
        try:
            return self.try_login(error_notice=error_notice)
        except KeyboardInterrupt as identifier:
            logging.warning('LoginHelper: Catch KeyboardInterrupt when logging in.')
            raise identifier
        except Exception:
            return False
