import requests
import os

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