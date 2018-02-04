import logging
from bs4 import BeautifulSoup
from ...config import AUTH_PASSWORD, AUTH_USERNAME
from .login_helper import LoginHelper

class AuthHelper(LoginHelper):
    def __init__(self, http_client):
        soup_checker = lambda soup: soup.title.text == '欢迎访问信息服务门户'
        super().__init__(http_client=http_client, soup_checker=soup_checker)

    def _login(self):
        login_url = r'https://auth.bupt.edu.cn/authserver/login?service=http%3A%2F%2Fmy.bupt.edu.cn%2Flogin.portal'
        login_soup = BeautifulSoup(self.http_client.get(login_url).text, 'lxml')
        logging.info(f'Auth login to: `{login_soup.title.text}`')
        args = {item['name']: item['value'] for item in login_soup.select('#casLoginForm input') if 'name' in item.attrs.keys()}
        args['username'] = AUTH_USERNAME
        args['password'] = AUTH_PASSWORD
        return self.http_client.post(login_url, data=args, referer='http://my.bupt.edu.cn/')
