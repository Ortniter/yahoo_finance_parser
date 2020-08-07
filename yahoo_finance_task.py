from selenium import webdriver
from time import sleep
from bs4 import BeautifulSoup
import requests
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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


class HistoricalDataParser(YahooFinanceBaseParser):
    def __init__(self, companies):
        super().__init__(companies)
        self.historical_data_columns = 'Date,Open,High,Low,Close,Adj Close,Volume'

    def get_html(self, url):
        """
        This method extracts html from historical data page
        :param url: historical data page url
        :return: html to parse
        """
        self.driver.get(url)

        time_period_btn = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[@class="Pos(r) D(ib) Va(m) Mstart(8px)"]')))
        time_period_btn.click()

        max_btn = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//button[@data-value="MAX"]')))
        max_btn.click()

        sleep(2)
        html = self.driver.page_source
        return html

    @staticmethod
    def get_historical_data_url(html, company):
        """
        This method extracts download link from historical data page
        :param html: historical data page html
        :param company: company's TICKER
        :return: url with all historical data
        """
        soup = BeautifulSoup(html, 'lxml')
        data_url = soup.find('a', download=f"{company}.csv").get('href').strip()
        return data_url

    @staticmethod
    def create_historical_data_dict(data):
        """
        This method maps date with a close_price and a row for future checks
        :param data: data from historical_data csv file
        :return: dict where date is a key that has a dict as a value with close_price and a row
        """
        separated_data = data.split('\n')
        data_dict = dict()

        for row in separated_data[1:]:
            if not row:
                continue
            else:
                date = row.split(',')[0]
                close_price = row.split(',')[4]
                data_dict[date] = {'close_price': close_price, 'row': row}
        if not data_dict:
            logger.error('Historical data dict was not prepared!')
            return False
        logger.debug('Dict with historical data has been created')
        return data_dict
