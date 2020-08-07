from selenium import webdriver
from bs4 import BeautifulSoup
import requests
from selenium.webdriver.firefox.options import Options
from logger import Logger

logger = Logger('yahoo_parser')


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
        logger.error(message=f'Failed to get HTML, code {response.status_code}:\n{response.text}')
        return False

    @staticmethod
    def write_csv(csv_data, file_name):
        """
        :param csv_data: data prepared to be written in csv file
        :param file_name: desired name of the file
        :return: None
        """
        with open(f'{file_name}.csv', 'a') as file:
            file.write(csv_data)
        logger.info(message=f'{file_name} saved')

    @staticmethod
    def get_company_name(html):
        """
        This method extracts company's name from html
        :param html: html of the news or history page
        :return: name without spaces or comas
        """
        soup = BeautifulSoup(html, 'lxml')
        company_name = soup.find('h1', attrs={'class': 'D(ib) Fz(18px)'}).text
        company_name = company_name.split('Inc')[0].strip()
        company_name = ''.join(company_name.split(' '))
        company_name = company_name.split(',')[0]
        return company_name

    def prepare_csv_data(self, data):
        raise NotImplementedError('Use parse_html method from child')

    def work(self):
        raise NotImplementedError('Use parse_html method from child')
