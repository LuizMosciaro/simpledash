from django.contrib.auth import authenticate, login
from django.contrib.gis.geoip2 import GeoIP2
from django.shortcuts import redirect, render
from geoip2.errors import AddressNotFoundError

from .forms import LoginForm, SignUpForm
from .utils import (get_btc, get_dolar, get_fundamentals,
                    get_highest_volume_stocks, get_historic_prices, get_ipca,
                    get_selic, get_weather)


def home(request):
    try:
        ip_results = None
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        
        g = GeoIP2()
        location = g.city(ip)
        location_country = location["country_name"]
        location_city = location["city"]
        ip_results = {
            "ip": ip,
            "location_country": location_country,
            "location_city": location_city,
        }
        
    except AddressNotFoundError:
        ip_results = None
        pass
    
    user = 'Luiz'
    price_data = get_historic_prices('petr4')
    context = {
        'user':user,
        "stock_chart_labels": price_data["labels"],
        "stock_chart_data": price_data["data"],
    }
    if ip_results:
        context.update(ip_results)
        context.update(get_weather(location_city))
        context.update(get_selic())
        
    context.update(get_ipca())
    context.update(get_dolar())
    context.update(get_btc())
    context.update(get_highest_volume_stocks())
    context.update(get_fundamentals('petr4'))
    
    if request.method == 'POST':
        if "symbol" in request.POST:
            ticker = str(request.POST['symbol']).replace("(","").replace(")","")
            context.update(get_fundamentals(ticker))
            price_data = get_historic_prices(ticker)
            context.update({'stock_chart_labels':price_data['labels']})
            context.update({'stock_chart_data':price_data['data']})

            return render(request,'home/index.html',context)
    
    return render(request,'home/index.html',context)

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            pass1 = form.cleaned_data['password']
            user = authenticate(request,username=username,password=pass1)
            if user is not None:
                login(request,user)
                return redirect('home')
            else:
                form.add_error(None,"Invalid credentials")
    else:
        form = LoginForm()
    return render(request,'home/login.html', {'form': form})

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login_view')
    else:
        form = SignUpForm()

    return render(request,'home/signup.html', {'form':form})