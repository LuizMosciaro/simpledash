import os
import ssl
from datetime import date, datetime

import requests
import urllib3
from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta
from workalendar.america import Brazil


class CustomHttpAdapter (requests.adapters.HTTPAdapter):
    # "Transport adapter" that allows us to use custom ssl_context.

    def __init__(self, ssl_context=None, **kwargs):
        self.ssl_context = ssl_context
        super().__init__(**kwargs)

    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = urllib3.poolmanager.PoolManager(
            num_pools=connections, maxsize=maxsize,
            block=block, ssl_context=self.ssl_context)

def get_legacy_session():
    ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    ctx.options |= 0x4  # OP_LEGACY_SERVER_CONNECT
    session = requests.session()
    session.mount('https://', CustomHttpAdapter(ctx))
    return session

def get_weather(city):
    api_key = os.getenv('WEATHER_API_KEY')
    call = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{city}?unitGroup=us&key={api_key}&contentType=json"
    response = requests.get(call)
    if response.status_code == 200:
        query = response.json()
        context = {
            'lat': query['latitude'],
            'long': query['longitude'],
            'feelslike': round((float(query['currentConditions']['feelslike']) - 32) * 5/9, 1),
            'temp': round((float(query['currentConditions']['temp']) - 32) * 5/9, 1),
            'humidity': str(query['currentConditions']['humidity']),
            'conditions': str(query['currentConditions']['conditions']).lower(),
            'sunrise': query['currentConditions']['sunrise'],
            'sunset': query['currentConditions']['sunset'],
        }
        return context
    else:
        return response.raise_for_status()

def get_selic():
    workdays = Brazil().get_working_days_delta(
        date(2023, 1, 1), date(2023, 12, 31))
    today = datetime.today().strftime('%d/%m/%Y')
    url = f'https://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados?formato=json&dataInicial={today}&dataFinal={today}'
    response = requests.get(url)
    interest = response.json()[0]['valor']
    return {'selic':f'{(1 + float(interest)/100) ** workdays - 1:.2%}'}

def get_ipca():
    date_today = datetime.today()
    date_str = date_today - relativedelta(months=1)
    if date_str.month < 10:
        dt = f'{date_str.year}0{date_str.month}'
    else:
        dt = f'{date_str.year}{date_str.month}'

    url = f'https://servicodados.ibge.gov.br/api/v3/agregados/7060/periodos/{dt}/variaveis/63|69|2265?localidades=N1[all]'
    response = get_legacy_session().get(url)
    dataJson = response.json()
    if dataJson:
        context = {
            'montly_inflation' : dataJson[0]['resultados'][0]['series'][0]['serie'][dt],
            'ytd_inflation' : dataJson[1]['resultados'][0]['series'][0]['serie'][dt],
            'past_12m_inflation' : dataJson[2]['resultados'][0]['series'][0]['serie'][dt]
        }
    else:
        date_today = datetime.today()
        date_str = date_today - relativedelta(months=2)
        if date_str.month < 10:
            dt = f'{date_str.year}0{date_str.month}'
        else:
            dt = f'{date_str.year}{date_str.month}'
        
        url = f'https://servicodados.ibge.gov.br/api/v3/agregados/7060/periodos/{dt}/variaveis/63|69|2265?localidades=N1[all]'
        response = get_legacy_session().get(url)
        dataJson = response.json()
        if dataJson:
            context = {
                'montly_inflation' : dataJson[0]['resultados'][0]['series'][0]['serie'][dt],
                'ytd_inflation' : dataJson[1]['resultados'][0]['series'][0]['serie'][dt],
                'past_12m_inflation' : dataJson[2]['resultados'][0]['series'][0]['serie'][dt]
            }
    return context

def get_ipca2():
    header = {'Content-Type': 'text/html; charset=utf-8'}
    response = requests.get('https://www.ibge.gov.br/indicadores',headers=header)
    soup = BeautifulSoup(response.content, 'html.parser')
    tds_ultimos = soup.find('td', class_='ultimo')
    month_inf = tds_ultimos.get_text().strip().replace(' ','').replace('Último','').replace('\n','').replace(',','.')[:5]

    tds_12months = soup.find('td', class_='desktop-tablet-only dozemeses')
    twelve_months_inf = tds_12months.get_text().strip().replace(' ','').replace('12meses','').replace('\n','').replace(',','.')[:5]

    tds_ytd = soup.find('td', class_='desktop-tablet-only ano')
    ytd_inf = tds_ytd.get_text().strip().replace(' ','').replace('Noano','').replace('\n','').replace(',','.')[:5]
    
    context = {
        'montly_inflation': month_inf,
        'ytd_inflation': twelve_months_inf,
        'past_12m_inflation': ytd_inf
    }
    return context

def get_dolar():
    cal = Brazil()
    dt = cal.add_working_days(datetime.today(),-1)
    today = dt.strftime('%m-%d-%Y')
    url = f"https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoDolarDia(dataCotacao=@dataCotacao)?@dataCotacao='"+ today + "'&$top=100&$format=json&$select=cotacaoCompra"
    response = requests.get(url)
    dolar = str(response.json()['value'][0]['cotacaoCompra'])[:4]
    return {'dolar': dolar}

def get_btc():
    url = 'https://brapi.dev/api/v2/crypto?coin=BTC&currency=BRL'
    response = requests.get(url)
    btc = response.json()['coins'][0]['regularMarketPrice']
    return {'btc':'{:,.2f}'.format(btc).replace('.', 'v').replace(',', '.').replace('v', ',')}

def get_highest_volume_stocks():
    url = 'https://brapi.dev/api/quote/list?sortBy=volume&sortOrder=desc&limit=50'
    response = requests.get(url)
    data_list = response.json()['stocks']
    context = []
    for data in data_list:
        mapped_data = {
            'stock_symbol': data['stock'],
            'stock_name': data['name'],
            'stock_close': float(data['close']),
            'stock_change': round(float(data['change']),2),
            'stock_volume': '{:,.2f}'.format(data["volume"]).replace('.', 'v').replace(',', '.').replace('v', ',') if data['volume'] else 'N.A.',
            'stock_market_cap': '{:,.2f}'.format(data["market_cap"]).replace('.', 'v').replace(',', '.').replace('v', ',') if data['market_cap'] else 'N.A.',
            'stock_logo': data['logo'],
            'stock_sector': data['sector'],
            }
        context.append(mapped_data)
    return {'stocks_data': context}

def get_quote(ticker):
    url = f'https://brapi.dev/api/quote/{ticker}?range=1d&interval=1d&fundamental=false&dividends=false'
    response = requests.get(url=url)
    resultados = response.json()['results']
    context = []
    for data in resultados:
        mapped_data = {
            'symbol': data['symbol'], # 'PETR4',
            'shortName': data['shortName'], # 'PETROBRAS   PN      N2',
            'longName': data['longName'], # 'Petróleo Brasileiro S.A. - Petrobras',
            'currency': data['currency'], # 'BRL',
            'regularMarketPrice': data['regularMarketPrice'], # 22.93,
            'regularMarketDayHigh': data['regularMarketDayHigh'], # 23.65,
            'regularMarketDayLow': data['regularMarketDayLow'], # 22.89,
            'regularMarketDayRange': data['regularMarketDayRange'], # '22.89 - 23.65',
            'regularMarketChange': round(float(data['regularMarketChange']),2), # -0.5799999,  
            'regularMarketChangePercent': round(float(data['regularMarketChangePercent']),2), # -2.467035, 
            'regularMarketTime': data['regularMarketTime'], # '2023-03-20T20:07:45.000Z',
            'marketCap': data['marketCap'], # 317335142400,
            'regularMarketVolume':  '{:,.2f}'.format(data["regularMarketVolume"]).replace('.', 'v').replace(',', '.').replace('v', ',') if data['regularMarketVolume'] else 'N.A.',
            'regularMarketPreviousClose': data['regularMarketPreviousClose'], # 23.51,
            'regularMarketOpen': data['regularMarketOpen'], # 23.51,
            'averageDailyVolume10Day': data['averageDailyVolume10Day'], # 66321590,
            'averageDailyVolume3Month': data['averageDailyVolume3Month'], # 66903138,
            'fiftyTwoWeekLowChange': data['fiftyTwoWeekLowChange'], # 2.1599998,
            'fiftyTwoWeekRange': data['fiftyTwoWeekRange'], # '20.77 - 38.39',
            'fiftyTwoWeekHighChange': data['fiftyTwoWeekHighChange'], # -15.459999,
            'fiftyTwoWeekHighChangePercent': data['fiftyTwoWeekHighChangePercent'], # -0.402709,
            'fiftyTwoWeekLow': data['fiftyTwoWeekLow'], # 20.77,
            'fiftyTwoWeekHigh': data['fiftyTwoWeekHigh'], # 38.39,
            'twoHundredDayAverage': data['twoHundredDayAverage'], # 28.416,
            'twoHundredDayAverageChange': data['twoHundredDayAverageChange'], # -5.486,
            'twoHundredDayAverageChangePercent': data['twoHundredDayAverageChangePercent'], # -0.19306025,
            'logourl': data['logourl'] #'https://s3-symbol-logo.tradingview.com/brasileiro-petrobras--big.svg'
        }
        context.append(mapped_data)

    return {'stocks_full_data': context}

def get_historic_prices(symbol):
    alphaavantage_api = os.getenv('ALPHA_AVANTAGE_API')
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={symbol}.SAO&apikey={alphaavantage_api}'
    response = requests.get(url)
    data_json = response.json()
    
    labels = [] #Dias
    data = [] #Preco
    for key,value in data_json["Time Series (Daily)"].items():
        labels.append(key)
        data.append(value['1. open'])
    
    context = {
        'labels':list(reversed(labels)),
        'data':list(reversed(data))
    }
    return context

def get_fundamentals(symbol):
    header = {
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
    }
    url = f'https://www.fundamentus.com.br/detalhes.php?papel={symbol}'
    response = requests.get(url,headers=header)
    soup = BeautifulSoup(response.content, 'html.parser')
    td_mkt_value = soup.find('td',class_='data w3').get_text().strip()
    stock_float = soup.find_all('table',class_='w728')[1].find_all('td')[-1].get_text().strip()
    pl = soup.find_all('table',class_='w728')[2].find_all('td',class_='data w2')[0].get_text().strip()
    vpa = soup.find_all('table',class_='w728')[2].find_all('td',class_='data w2')[3].get_text().strip()
    roe = soup.find_all('table',class_='w728')[2].find_all('td',class_='data')[23].get_text().strip()
    context = {
        'td_mkt_value':str(td_mkt_value).replace(',','.'),
        'stock_float':str(stock_float).replace(',','.'),
        'pl':str(pl).replace(',','.'),
        'vpa':str(vpa).replace(',','.'),
        'roe':str(roe).replace(',','.'),
        }
    return context
