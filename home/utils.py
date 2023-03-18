import os
import requests
from datetime import date
from workalendar.america import Brazil
from datetime import datetime
from dateutil.relativedelta import relativedelta
import urllib3
import ssl

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

    date_str = datetime.today()
    date_str = date_str - relativedelta(months=1)
    if date_str.month < 10:
        dt = f'{date_str.year}0{date_str.month}'
    else:
        dt = f'{date_str.year}{date_str.month}'


    url = f'https://servicodados.ibge.gov.br/api/v3/agregados/7060/periodos/{dt}/variaveis/63|69|2265?localidades=N1[all]'
    response = get_legacy_session().get(url)
    dataJson = response.json()
    context = {
        'montly_inflation' : dataJson[0]['resultados'][0]['series'][0]['serie'][dt],
        'ytd_inflation' : dataJson[1]['resultados'][0]['series'][0]['serie'][dt],
        'past_12m_inflation' : dataJson[2]['resultados'][0]['series'][0]['serie'][dt]
    }
    return context