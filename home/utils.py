import os
import requests
from datetime import date
from workalendar.america import Brazil
from datetime import datetime


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
    date_str = datetime.today()
    if date_str.month < 10:
        date_str_month = '0' + str(date_str.month)
        dt = f'{date_str.year}{date_str_month}'
    else:
        dt = f'{date_str.year}{date_str_month}'

    url = f'https://servicodados.ibge.gov.br/api/v3/agregados/7060/periodos/{dt}/variaveis/63|69|2265?localidades=N1[all]'
    response = requests.get(url)
    context = {
        'montly_inflation' : response.json()[0]['resultados']['series']['serie'],
        'ytd_inflation' : response.json()[1]['resultados']['series']['serie'],
        'past_12m_inflation' : response.json()[2]['resultados']['series']['serie']
    }
    return context