import os
from datetime import datetime
from http import HTTPStatus
from unittest.mock import Mock, patch

import requests
from dateutil.relativedelta import relativedelta
from django.test import TestCase
from workalendar.america import Brazil

from home.utils import (get_btc, get_dolar, get_fundamentals,
                        get_highest_volume_stocks, get_historic_prices,
                        get_ipca, get_ipca2, get_legacy_session, get_quote, 
                        get_selic, get_weather)


class WeatherTestCase(TestCase):

    def test_get_weather_http_status_code(self):
        city = 'Manaus'
        api_key = os.getenv('WEATHER_API_KEY')
        call = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{city}?unitGroup=us&key={api_key}&contentType=json"
        response = requests.get(call)
        
        self.assertEqual(response.status_code,HTTPStatus.OK)
        self.assertIn('application/json',response.headers['Content-type'])

    def test_get_weather(self):
        city = 'Manaus'
        expected_keys = ['lat', 'long', 'feelslike', 'temp', 'humidity', 'conditions', 'sunrise', 'sunset']
        context = get_weather(city)

        self.assertIsInstance(context, dict)
        self.assertCountEqual(context.keys(), expected_keys)

class SelicTestCase(TestCase):
    
    def test_get_selic_http_status_code(self):
        today = datetime.today().strftime('%d/%m/%Y')
        url = f'https://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados?formato=json&dataInicial={today}&dataFinal={today}'
        response = requests.get(url)
        
        self.assertEqual(response.status_code,HTTPStatus.OK)
        self.assertIn('application/json',response.headers['Content-Type'])

    def test_get_selic(self):
        context = get_selic()
        
        self.assertIsInstance(context, dict)
        self.assertIn("selic",context)
        self.assertRegex(context['selic'],r"\d{2}.\d{2}\%")

class IPCATestCase(TestCase):

    def test_get_ipca_http_response(self):
        url = f'https://servicodados.ibge.gov.br/api/v3/agregados/7060/periodos/202301/variaveis/63|69|2265?localidades=N1[all]'
        response = get_legacy_session().get(url,timeout=100)

        self.assertEqual(response.status_code,HTTPStatus.OK)
        self.assertIn('application/json',response.headers['Content-type'])

    @patch('requests.get')
    def test_get_ipca(self,mock_session):
        mock_response = Mock()
        mock_data = [{
            'resultados': [
                {
                    'series':[
                        {
                            'serie': {
                                "202302":"0.84"
                            }
                        }
                    ]
                }
            ]
        },
        {
            'resultados': [
                {
                    'series':[
                        {
                            'serie': {
                                "202302":"1.37"
                            }
                        }
                    ]
                }
            ]
        },
        {
            'resultados': [
                {
                    'series':[
                        {
                            'serie': {
                                "202302":"5.60"
                            }
                        }
                    ]
                }
            ]
        }]

        mock_response.json.return_value = mock_data
        mock_session.return_value.get.return_value = mock_response
        context = get_ipca()
        expected_keys = ['monthly_inflation','ytd_inflation','past_12m_inflation']
        for value in context.keys():
            self.assertIsInstance(value,str)

        self.assertCountEqual(context.keys(),expected_keys)
        self.assertAlmostEqual(context['monthly_inflation'], "0.84")
        self.assertAlmostEqual(context['ytd_inflation'], "1.37")
        self.assertAlmostEqual(context['past_12m_inflation'], "5.60")

class IPCATestCase2(TestCase):
    def test_get_ipca2_http_response(self):
        url = f'https://servicodados.ibge.gov.br/api/v3/agregados/7060/periodos/202301/variaveis/63|69|2265?localidades=N1[all]'
        response = get_legacy_session().get(url,timeout=100)

        self.assertEqual(response.status_code,HTTPStatus.OK)
        self.assertIn('application/json',response.headers['Content-type'])

    @patch('requests.get')
    def test_get_ipca2(self,mock_session):
        mock_response = mock_session.return_value
        mock_response.content = '\
        <html>\
            <td class="ultimo">Último 10,00</td>\
            <td class="desktop-tablet-only dozemeses">12 meses 20,00</td>\
            <td class="desktop-tablet-only ano">No ano 30,00</td>\
        </html>'

        result = get_ipca2()
        expected_keys = ['monthly_inflation','ytd_inflation','past_12m_inflation']
        self.assertIsInstance(result, dict)
        self.assertCountEqual(expected_keys,result.keys())
        

class DolarTestCase(TestCase):
    
    def test_get_dolar_http_response(self):
        cal = Brazil()
        dt = cal.add_working_days(datetime.today(),-1)
        today = dt.strftime('%m-%d-%Y')
        url = f"https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoDolarDia(dataCotacao=@dataCotacao)?@dataCotacao='"+ today + "'&$top=100&$format=json&$select=cotacaoCompra"
        response = requests.get(url)

        self.assertEqual(response.status_code,HTTPStatus.OK)
        self.assertIn('application/json',response.headers['Content-type'])
    
    @patch('requests.get')
    def test_get_dolar(self,mock_session):
        mock_response = Mock()
        mock_data = {
            'value': [
                {
                    'cotacaoCompra':"5.2915"
                }
            ]
        }
        mock_response.json.return_value = mock_data
        mock_session.return_value = mock_response

        context = get_dolar()

        self.assertIsInstance(context,dict)
        self.assertIsInstance(context['dolar'],str)
        self.assertIn('dolar',context)
        self.assertEqual(context,{'dolar':'5.29'})

class TestCryptoAPI(TestCase):

    def test_get_dolar_http_response(self):
        url = 'https://brapi.dev/api/v2/crypto?coin=BTC&currency=BRL'
        response = requests.get(url)

        self.assertEqual(response.status_code,HTTPStatus.OK)
        self.assertIn('application/json',response.headers['Content-type'])

    @patch('requests.get')
    def test_get_btc_success(self, mock_get):
        mock_response = Mock()
        mock_data = {
            'coins':[
                {
                    'regularMarketPrice': 144455.083564
                }
            ]
        }
        mock_response.json.return_value = mock_data
        mock_get.return_value = mock_response
        
        expected = {'btc': '144.455,08'}
        context = get_btc()

        self.assertIn('btc',context)
        self.assertEqual(context, expected)
        self.assertIsInstance(context,dict)
        self.assertIsInstance(context['btc'],str)

class TestHighestVolumeStocks(TestCase):
    
    def test_get_highest_volumes_stocks_http_response(self):
        url = 'https://brapi.dev/api/quote/list?sortBy=volume&sortOrder=desc&limit=50'
        response = requests.get(url)

        self.assertIn('application/json',response.headers['Content-type'])
        self.assertEqual(response.status_code,HTTPStatus.OK)
    
    @patch('requests.get')
    def test_get_highest_volume_stocks(self,mock_session):
        mock_response = Mock()
        mock_data = {
            'stocks':[
                {
                    "stock": "MGLU3",
                    "name": "MAGAZINE LUIZA",
                    "close": 3.23,
                    "change": 3.8585209,
                    "volume": 118058300,
                    "market_cap": 21569430708,
                    "logo": "https://s3-symbol-logo.tradingview.com/magaz-luiza-on-nm--big.svg",
                    "sector": "Retail Trade"
                },
                {
                    "stock": "VIIA3",
                    "name": "VIA",
                    "close": 1.87,
                    "change": 1.08108108,
                    "volume": 54154700,
                    "market_cap": 2988505399,
                    "logo": "https://s3-symbol-logo.tradingview.com/via--big.svg",
                    "sector": "Retail Trade"
                }
            ]
        }

        mock_response.json.return_value = mock_data
        mock_session.return_value = mock_response

        context = get_highest_volume_stocks()

        self.assertIsInstance(context,dict)
        self.assertIsInstance(context['stocks_data'],list)
        for stock_data in context['stocks_data']:
            self.assertIsInstance(stock_data['stock_symbol'], str)
            self.assertIsInstance(stock_data['stock_name'], str)
            self.assertIsInstance(stock_data['stock_close'], float)
            self.assertIsInstance(stock_data['stock_change'], float)
            self.assertIsInstance(stock_data['stock_volume'], str)
            self.assertIsInstance(stock_data['stock_market_cap'], str)
            self.assertIsInstance(stock_data['stock_logo'], str)
            self.assertIsInstance(stock_data['stock_sector'], str)

class GetQuoteTest(TestCase):
    
    def test_get_quote_http_response(self):
        url = f'https://brapi.dev/api/quote/PETR3?range=1d&interval=1d&fundamental=false&dividends=false'
        response = requests.get(url=url)

        self.assertIn('application/json',response.headers['Content-type'])
        self.assertEqual(response.status_code,HTTPStatus.OK)

    @patch('requests.get')
    def test_get_quote(self,mock_session):
        mock_response = Mock()
        mock_data = {
            'results':[{
                "symbol": "PETR3",
                "shortName": "PETROBRAS   ON      N2",
                "longName": "Petróleo Brasileiro S.A. - Petrobras",
                "currency": "BRL",
                "regularMarketPrice": 25.66,
                "regularMarketDayHigh": 26.65,
                "regularMarketDayLow": 25.43,
                "regularMarketDayRange": "0.0 - 0.0",
                "regularMarketChange": 0.09000015,
                "regularMarketChangePercent": 0.3519756,
                "regularMarketTime": "2023-03-24T20:07:30.000Z",
                "marketCap": 318635606016,
                "regularMarketVolume": 452239999,
                "regularMarketPreviousClose": 25.57,
                "regularMarketOpen": 25.76,
                "averageDailyVolume10Day": 12824900,
                "averageDailyVolume3Month": 14314237,
                "fiftyTwoWeekLowChange": 25.66,
                "fiftyTwoWeekRange": "0.0 - 42.08",
                "fiftyTwoWeekHighChange": -16.420002,
                "fiftyTwoWeekHighChangePercent": -0.39020917,
                "fiftyTwoWeekLow": 56.11,
                "fiftyTwoWeekHigh": 42.08,
                "twoHundredDayAverage": 31.56115,
                "twoHundredDayAverageChange": -5.9011497,
                "twoHundredDayAverageChangePercent": -0.18697512,
                "logourl": "https://s3-symbol-logo.tradingview.com/brasileiro-petrobras--big.svg"
            }]
        }
        mock_response.json.return_value = mock_data
        mock_session.return_value = mock_response

        context = get_quote('PETR3')

        self.assertIsInstance(context,dict)
        self.assertIsInstance(context['stocks_full_data'],list)
        for stocks_full_data in context['stocks_full_data']:
            self.assertIsInstance(stocks_full_data['symbol'],str)
            self.assertIsInstance(stocks_full_data['shortName'],str)
            self.assertIsInstance(stocks_full_data['longName'],str)
            self.assertIsInstance(stocks_full_data['currency'],str)
            self.assertIsInstance(stocks_full_data['regularMarketPrice'],float)
            self.assertIsInstance(stocks_full_data['regularMarketDayHigh'],float)
            self.assertIsInstance(stocks_full_data['regularMarketDayLow'],float)
            self.assertIsInstance(stocks_full_data['regularMarketDayRange'],str)
            self.assertIsInstance(stocks_full_data['regularMarketChange'],float)
            self.assertIsInstance(stocks_full_data['regularMarketChangePercent'],float)
            self.assertIsInstance(stocks_full_data['regularMarketTime'],str)
            self.assertIsInstance(stocks_full_data['marketCap'],int)
            self.assertIsInstance(stocks_full_data['regularMarketVolume'],str)
            self.assertIsInstance(stocks_full_data['regularMarketPreviousClose'],float)
            self.assertIsInstance(stocks_full_data['regularMarketOpen'],float)
            self.assertIsInstance(stocks_full_data['averageDailyVolume10Day'],int)
            self.assertIsInstance(stocks_full_data['averageDailyVolume3Month'],int)
            self.assertIsInstance(stocks_full_data['fiftyTwoWeekLowChange'],float)
            self.assertIsInstance(stocks_full_data['fiftyTwoWeekRange'],str)
            self.assertIsInstance(stocks_full_data['fiftyTwoWeekHighChange'],float)
            self.assertIsInstance(stocks_full_data['fiftyTwoWeekHighChangePercent'],float)
            self.assertIsInstance(stocks_full_data['fiftyTwoWeekLow'],float)
            self.assertIsInstance(stocks_full_data['fiftyTwoWeekHigh'],float)
            self.assertIsInstance(stocks_full_data['twoHundredDayAverage'],float)
            self.assertIsInstance(stocks_full_data['twoHundredDayAverageChange'],float)
            self.assertIsInstance(stocks_full_data['twoHundredDayAverageChangePercent'],float)
            self.assertIsInstance(stocks_full_data['logourl'],str)

class HistoricPricesTestCase(TestCase):

    def test_get_historic_prices_http_response(self):

        alphaavantage_api = os.getenv('ALPHA_AVANTAGE_API')
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=PETR3.SAO&apikey={alphaavantage_api}'
        response = requests.get(url)

        self.assertIn('application/json',response.headers['Content-type'])
        self.assertEqual(response.status_code,HTTPStatus.OK)

    @patch('requests.get')
    def test_get_historic_prices(self,mock_session):
        mock_response = Mock()
        mock_data = {
            'Time Series (Daily)': {
                "2023-03-24": {
                    "1. open": "25.57",
                    "2. high": "25.94",
                    "3. low": "25.25",
                    "4. close": "25.66",
                    "5. adjusted close": "25.66",
                    "6. volume": "11495300",
                    "7. dividend amount": "0.0000",
                    "8. split coefficient": "1.0"
                },
                "2023-03-23": {
                    "1. open": "26.18",
                    "2. high": "26.55",
                    "3. low": "25.43",
                    "4. close": "25.57",
                    "5. adjusted close": "25.57",
                    "6. volume": "16280300",
                    "7. dividend amount": "0.0000",
                    "8. split coefficient": "1.0"
                }
            }
        }
        mock_response.json.return_value = mock_data
        mock_session.return_value = mock_response

        context = get_historic_prices('PETR3')

        self.assertIsInstance(context,dict)
        self.assertIsInstance(context['labels'],list)
        self.assertIsInstance(context['data'],list)
        self.assertEqual(context['labels'][0],"2023-03-23") #list is reversed
        self.assertEqual(context['data'][0],"26.18") #list is reversed

class FundamentalsTest(TestCase):

    def test_get_fundamentals_http_response(self):
        header = {
            "Accept": "*/*",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
        }
        url = f'https://www.fundamentus.com.br/detalhes.php?papel=PETR3'
        response = requests.get(url,headers=header)

        self.assertIn('text/html',response.headers['Content-type'])
        self.assertEqual(response.status_code,HTTPStatus.OK)
    
    def test_get_fundamentals(self):
        symbol = 'PETR3'
        response = get_fundamentals(symbol)
        expected_keys = ['td_mkt_value', 'stock_float', 'pl', 'vpa', 'roe']
        for key in expected_keys:
            self.assertIn(key,response)
            self.assertIsInstance(response[key],str)