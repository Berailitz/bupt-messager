import logging
import time
from io import BytesIO
import pytesseract
from bs4 import BeautifulSoup
from PIL import Image
from ...config import WEB_VPN_ALLOW_ERROR, WEB_VPN_PASSWORD, WEB_VPN_USERNAME
from .login_helper import LoginHelper

class WebVPNHelper(LoginHelper):
    def __init__(self, http_client, tesseract_cmd):
        self.allow_error = WEB_VPN_ALLOW_ERROR
        soup_checker = lambda soup: soup.title.text == '校园访问校园网门户' or (self.allow_error and 'Error' in soup.title.text)
        super().__init__(http_client=http_client, soup_checker=soup_checker)
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    @staticmethod
    def read_webvpn_captcha(im_raw):
        im_l = im_raw.convert('L')
        threshold = 1
        im_b = im_l.point([0] * threshold + [255] * (256 - threshold))
        return pytesseract.image_to_string(im_b, config='-c tessedit_char_whitelist=0123456789 -psm 7')

    def solve_webvpn_captcha(self):
        webvpn_captcha_url = 'http://webvpn.bupt.edu.cn/wengine-auth/captcha/'
        captcha_img = Image.open(BytesIO(self.http_client.get(webvpn_captcha_url, referer='http://webvpn.bupt.edu.cn/').content))
        captcha_text = self.read_webvpn_captcha(captcha_img)
        logging.info(f'Web VPN captcha: {captcha_text}')
        return captcha_text

    def _login(self):
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
