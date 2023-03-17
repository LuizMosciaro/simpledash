from django.shortcuts import render
from django.contrib.gis.geoip2 import GeoIP2
from .utils import get_weather

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
    context = {
        'user':'Luiz',
        "ip": ip,
        "location_country": location_country,
        "location_city": location_city
    }
    context.update(get_weather(location_city))
    
    return render(request,'home/index.html',context)