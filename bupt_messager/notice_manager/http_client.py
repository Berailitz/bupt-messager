"""HTTP layer."""
import logging
import requests
from ..config import HTTP_CLIENT_MAX_RETRIES, HTTP_CLIENT_REFERER, HTTP_CLIENT_TIME_OUT


class HTTPClient:
    """Client for HTTP requests..

    :member session: Attached Requests session.
    """
    def __init__(self, session=None):
        if session:
            self.session = session
        else:
            self.session = requests.Session()

    @staticmethod
    def create_headers(referer='http://my.bupt.edu.cn/index.portal', origin='http://my.bupt.edu.cn/index.portal'):
        """Create http headers with custom `referer` and `origin`.
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4',
            'Connection': 'keep-alive',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Cache-Control': 'max-age=0',
            'Referer': referer,
            'Origin': origin
        }
        return headers

    def post(self, url, data, timeout=HTTP_CLIENT_TIME_OUT, max_retries=HTTP_CLIENT_MAX_RETRIES, referer=HTTP_CLIENT_REFERER, **kw):
        """Post with headers.
        """
        for attempt_counter in range(max_retries):
            try:
                post_response = self.session.post(url, headers=self.create_headers(referer), data=data, timeout=timeout, **kw)
                post_response.encoding = "utf-8"
                return post_response
            except requests.Timeout as identifier:
                logging.warning(f'HTTPClient: ({attempt_counter + 1} / {max_retries}) Failed to POST `{data}` to `{url}`: {identifier}')
                attempt_counter += 1
        raise requests.Timeout(f'HTTPClient: Max POST retries exceeded with url: {url}')

    def get(self, url, timeout=HTTP_CLIENT_TIME_OUT, max_retries=HTTP_CLIENT_MAX_RETRIES, referer=HTTP_CLIENT_REFERER, **kw):
        """Get with headers.
        """
        for attempt_counter in range(max_retries):
            try:
                get_response = self.session.get(url, headers=self.create_headers(referer), timeout=timeout, **kw)
                get_response.encoding = "utf-8"
                return get_response
            except requests.Timeout as identifier:
                logging.warning(f'HTTPClient: ({attempt_counter + 1} / {max_retries}) Failed to GET `{url}`: {identifier}')
                attempt_counter += 1
        raise requests.Timeout(f'HTTPClient: Max GET retries exceeded with url: {url}')

    def refresh_session(self, session=None):
        """Generate a new session or set a new session.

        :param session: New session, defaults to None.
        :type session: Requests.Session, optional.
        """
        self.session = session or requests.Session()
        logging.warning('HTTPClient: session refreshed.')
