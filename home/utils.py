import os
import requests
from datetime import date
from workalendar.america import Brazil
from datetime import datetime
from dateutil.relativedelta import relativedelta
from bs4 import BeautifulSoup
import time
import requests
import urllib3
import ssl


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
            'sensacao_term': round((float(query['currentConditions']['feelslike']) - 32) * 5/9, 1),
            'temp': round((float(query['currentConditions']['temp']) - 32) * 5/9, 1),
            'humidade': str(query['currentConditions']['humidity']) + '%',
            'condicao': query['currentConditions']['conditions'],
            'raiar_sol': query['currentConditions']['sunrise'],
            'anoitecer': query['currentConditions']['sunset'],
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
    header = {'Content-Type': 'text/html; charset=utf-8'}
    response = get_legacy_session().get('https://www.ibge.gov.br/indicadores',headers=header)
    #response = requests.get('https://www.ibge.gov.br/indicadores',headers=header)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    tds_ultimos = soup.find('td', class_='ultimo')
    month_inf = tds_ultimos.get_text().strip().replace(' ','').replace('Último','').replace('\n','').replace(',','.')[:5]

    tds_12months = soup.find('td', class_='desktop-tablet-only dozemeses')
    past_12m_inflation = tds_12months.get_text().strip().replace(' ','').replace('12meses','').replace('\n','').replace(',','.')[:5]

    tds_ytd = soup.find('td', class_='desktop-tablet-only ano')
    ytd_inf = tds_ytd.get_text().strip().replace(' ','').replace('Noano','').replace('\n','').replace(',','.')[:5]
    context = {
        'montly_inflation': month_inf,
        'ytd_inflation': ytd_inf,
        'past_12m_inflation': past_12m_inflation
    }
    return context