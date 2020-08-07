from yahoo_finance_task import YahooFinanceBaseParser, HistoricalDataParser, LatestNewsParser
from unittest import TestCase
from unittest.mock import MagicMock

companies_list = ['PD']

row = '2017-04-28,17.799999,19.330000,17.730000,18.100000,18.100000,14871500'
data_dict = {'2017-04-28': {'close_price': '18.100000', 'row': row}}


class TestYahooFinanceBaseParser(TestCase):
    def setUp(self):
        self.base_parser = YahooFinanceBaseParser(companies_list)

    def tearDown(self):
        self.base_parser.driver.quit()

    def test_get_company_name(self):
        html = '<h1 class="D(ib) Fz(18px)">Zoom Video Communications, Inc. (ZM)</h1>'
        name = self.base_parser.get_company_name(html)
        self.assertEqual(name, 'ZoomVideoCommunications')
        self.assertRaises(AttributeError, self.base_parser.get_company_name, 'Not HTML')
        self.assertNotIn(' ', name)

    def test_not_implemented_methods(self):
        self.assertRaises(NotImplementedError, self.base_parser.get_html, 'url')
        self.assertRaises(NotImplementedError, self.base_parser.prepare_csv_data, 'data')
        self.assertRaises(NotImplementedError, self.base_parser.work)


class TestHistoricalDataParser(TestCase):
    def setUp(self):
        self.historical_parser = HistoricalDataParser(companies_list)
        self.historical_parser.get_html = MagicMock()
        self.historical_parser.get_historical_data_url = MagicMock()
        self.historical_parser.get_response = MagicMock()
        self.historical_parser.write_csv = MagicMock()

    def tearDown(self):
        self.historical_parser.driver.quit()

    def test_create_historical_data_dict(self):
        data = 'Date,Open,High,Low,Close,Adj Close,Volume\n' \
               '2017-04-28,17.799999,19.330000,17.730000,18.100000,18.100000,14871500\n'
        expected_data = data_dict
        self.assertEqual(self.historical_parser.create_historical_data_dict(data), expected_data)
        self.assertFalse(self.historical_parser.create_historical_data_dict('not data'))

    def test_get_previous_date(self):
        date, day = '2017-06-22', 3
        self.assertEqual(self.historical_parser.get_previous_date(date, day), '2017-06-19')
        date, day = '2017-13-22', 3
        self.assertRaises(ValueError, self.historical_parser.get_previous_date, date, day)

    def test_prepare_csv_data(self):
        expected_data = 'Date,Open,High,Low,Close,Adj Close,Volume,3day_before_change\n' \
                        '2017-04-28,17.799999,19.330000,17.730000,18.100000,18.100000,14871500,-\n'
        self.assertEqual(self.historical_parser.prepare_csv_data(data_dict), expected_data)
        self.assertRaises(AttributeError, self.historical_parser.prepare_csv_data, 'not data_dict')

    def test_work(self):
        self.historical_parser.create_historical_data_dict = MagicMock()
        self.historical_parser.prepare_csv_data = MagicMock()
        self.historical_parser.get_company_name = MagicMock()
        self.historical_parser.work()
        self.historical_parser.create_historical_data_dict.assert_called_once()
        self.historical_parser.prepare_csv_data.assert_called_once()
        self.historical_parser.get_company_name.assert_called_once()
        self.historical_parser.get_html.assert_called_once()
        self.historical_parser.get_historical_data_url.assert_called_once()
        self.historical_parser.get_response.assert_called_once()
        self.historical_parser.write_csv.assert_called_once()
