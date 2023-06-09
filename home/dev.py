import os
import ssl
from datetime import date, datetime

import numpy as np
import requests
import urllib3
from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta
from workalendar.america import Brazil


def get_last_business_day():
    today = datetime.today().date()
    if np.is_busday(today):
        return today
    else:
        last_business_day = np.busday_offset(today, -1, roll='backward')
        return last_business_day
    
def get_selic():
    try:
        workdays = Brazil().get_working_days_delta(
            date(date.today().year, 1, 1), date(date.today().year, 12, 31))
        dt = get_last_business_day()
        today = dt.strftime('%d-%m-%Y')
        url = f'https://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados?formato=json&dataInicial={today}&dataFinal={today}'
        response = requests.get(url)
        interest = response.json()[0]['valor']
        print(interest,url)
        return {'selic':f'{(1 + float(interest)/100) ** workdays - 1:.2%}'}
    except Exception:
        return {'selic':'null'}

print(get_selic())