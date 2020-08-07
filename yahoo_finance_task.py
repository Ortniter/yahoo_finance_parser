from selenium import webdriver

import requests
from selenium.webdriver.firefox.options import Options


class YahooFinanceBaseParser:
    def __init__(self, companies):
        """
        :param companies:takes list with companies TICKERS
        """
        options = Options()
        options.headless = True
        self.driver = webdriver.Firefox(options=options)
        self.companies = companies
        self.base_url = 'https://finance.yahoo.com'

    def get_html(self, url):
        raise NotImplementedError('Use parse_html method from child')

    @staticmethod
    def get_response(url):
        """
        :param url: takes url
        :return: response from url or False if status_code == 200
        """
        response = requests.get(url)
        if response.status_code == 200:
            return response
        return False
