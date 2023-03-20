from django.shortcuts import render
from django.contrib.gis.geoip2 import GeoIP2
from .utils import get_weather,get_selic,get_ipca,get_dolar,get_btc

def home(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    
    g = GeoIP2()
    location = g.city(ip)
    location_country = location["country_name"]
    location_city = location["city"]
    user = 'Luiz'
    context = {
        'user':user,
        "ip": ip,
        "location_country": location_country,
        "location_city": location_city
    }
    context.update(get_weather(location_city))
    context.update(get_selic())
    context.update(get_ipca())
    context.update(get_dolar())
    context.update(get_btc())
    
    return render(request,'home/index.html',context)