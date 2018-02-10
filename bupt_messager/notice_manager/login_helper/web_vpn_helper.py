"""Logic about web VPN."""
import logging
import time
from io import BytesIO
import pytesseract
from bs4 import BeautifulSoup
from PIL import Image
from ...config import TESSERACT_CMD, WEB_VPN_ALLOW_ERROR, WEB_VPN_PASSWORD, WEB_VPN_USERNAME
from .login_helper import LoginHelper


class WebVPNHelper(LoginHelper):
    """Connnect to web VPN.
    """
    def __init__(self, http_client):
        """Set `http_client`, read `TESSERACT_CMD` and `WEB_VPN_ALLOW_ERROR` from config.
        """
        self.allow_error = WEB_VPN_ALLOW_ERROR
        super().__init__(http_client=http_client)
        if TESSERACT_CMD:
            pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

    def response_checker(self, login_response):
        """Check if result, try login for .

        :return: Error description.
        :rtype: str|None.
        """
        correct_title = '校园访问校园网门户'
        if login_response.status_code == 200:
            try:
                login_soup = BeautifulSoup(login_response.text, 'lxml')
                if not login_soup.title:
                    logging.warning('Web VPN: No title detected.')
                    if self.allow_error:
                        return None
                    else:
                        return 'Login result: No title detected.'
                if login_soup.title.text == correct_title:
                    logging.warning(f'Web VPN: title `{login_soup.title.text}`.')
                    return None
                else:
                    return f'Login result: `{login_soup.title.text}`'
            except KeyboardInterrupt as identifier:
                logging.warning('Catch KeyboardInterrupt when logging into web VPN.')
                raise identifier
            except Exception as identifier:
                logging.exception(identifier)
                return identifier
        else:
            if self.allow_error:
                logging.warning('Web VPN: server error: `{login_response.status_code}`')
                return None
            else:
                return f'Login response: `{login_response.status_code}`'

    @staticmethod
    def read_webvpn_captcha(im_raw):
        """Read text from captcha image.

        :param im_raw: captcha image.
        :type im_raw: PIL.Image.
        :return: Text in captcha.
        :rtype: str.
        """
        im_l = im_raw.convert('L')
        threshold = 1
        im_b = im_l.point([0] * threshold + [255] * (256 - threshold))
        return pytesseract.image_to_string(im_b, config='-c tessedit_char_whitelist=0123456789 -psm 7')

    def solve_webvpn_captcha(self):
        """Download captcha image and read it.

        :return: captcha text.
        :rtype: str.
        """
        webvpn_captcha_url = 'http://webvpn.bupt.edu.cn/wengine-auth/captcha/'
        captcha_img = Image.open(BytesIO(self.http_client.get(webvpn_captcha_url, referer='http://webvpn.bupt.edu.cn/').content))
        captcha_text = self.read_webvpn_captcha(captcha_img)
        logging.info(f'Web VPN captcha: {captcha_text}')
        return captcha_text

    def _login(self):
        """Send login request.
        """
        login_page_url = 'http://webvpn.bupt.edu.cn/'
        login_form_url = 'http://webvpn.bupt.edu.cn/wengine-auth/login/'
        login_payload = {'username': WEB_VPN_USERNAME, 'password': WEB_VPN_PASSWORD, 'captcha': self.solve_webvpn_captcha()}
        login_page_response = self.http_client.get(login_page_url, referer=login_page_url)
        logging.info(f"Web VPN login to: `{BeautifulSoup(login_page_response.text, 'lxml').title.text}`")
        logging.info('Waiting to login to web VPN.')
        time.sleep(5)
        login_response = self.http_client.post(login_form_url, referer='http://webvpn.bupt.edu.cn/wengine-auth/login/', data=login_payload)
        logging.info(f'Web VPN login status: {login_response.status_code}')
        return login_response
