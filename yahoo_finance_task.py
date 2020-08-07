from selenium import webdriver
from time import sleep
from bs4 import BeautifulSoup
import requests
import datetime
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
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

    @staticmethod
    def get_previous_date(date, days):
        """
        :param date: takes date as str
        :param days: quantity of days
        :return: previous_date
        """
        year, month, day = date.split('-')
        current_date = datetime.date(int(year), int(month), int(day))
        previous_date = current_date - datetime.timedelta(days=days)
        previous_date = str(previous_date)
        return previous_date

    def prepare_csv_data(self, data_dict):
        """
        This method prepares data to be witten to new csv file
        :param data_dict: takes dict where date is a key that has a dict as a value with close_price and a row
        :return: csv_data
        """
        csv_data = f'{self.historical_data_columns},3day_before_change\n'
        for key, value in data_dict.items():
            previous_date = self.get_previous_date(key, 3)
            if previous_date in data_dict:
                current_close_price = float(value['close_price'])
                previous_close_price = float(data_dict[previous_date]['close_price'])
                three_day_before_change = round(current_close_price / previous_close_price, 6)
            else:
                three_day_before_change = '-'
            csv_data += f"{value['row']},{three_day_before_change}\n"
        return csv_data

    def work(self):
        if not os.path.exists('historical_data'):
            os.mkdir('historical_data')
        for company in self.companies:
            html = self.get_html(f'{self.base_url}/quote/{company}/history?p={company}')
            url = self.get_historical_data_url(html, company)
            data = self.get_response(url).text
            data_dict = self.create_historical_data_dict(data)
            csv_data = self.prepare_csv_data(data_dict)
            company_name = self.get_company_name(html)
            self.write_csv(csv_data, f'historical_data/{company_name}')
        self.driver.quit()


class LatestNewsParser(YahooFinanceBaseParser):
    def __init__(self, companies):
        super().__init__(companies)

    def get_html(self, url):
        """
        This method extracts html from summary page
        :param url: summary page url
        :return: html to parse
        """
        self.driver.get(url)
        sleep(2)
        html = self.driver.page_source
        return html

    def prepare_csv_data(self, html):
        """
        This method prepares data to be witten to new csv file
        :param html: takes html from summary page
        :return: csv_data
        """
        soup = BeautifulSoup(html, 'lxml')
        heads = soup.find_all('h3', attrs={'class': 'Mb(5px)'})
        csv_data = 'Link,Title\n'
        for head in heads:
            a_tag = head.find('a')
            href = a_tag.get('href')
            url = f'{self.base_url}{href}'
            title = a_tag.text
            title = ' '.join(title.split(','))
            csv_data += f'{url},{title}\n'
        return csv_data
