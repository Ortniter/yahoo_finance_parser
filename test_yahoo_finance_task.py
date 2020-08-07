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



