from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.contrib.gis.geoip2 import GeoIP2
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from geoip2.errors import AddressNotFoundError

from .forms import LoginForm, SignUpForm, NewAssetForm
from .models import Asset
from .utils import (get_btc, get_dolar, get_fundamentals,
                    get_highest_volume_stocks, get_historic_prices, get_ipca2,
                    get_selic, get_weather)

@cache_page(30000) #+-8.5hrs
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
        
    #context.update(get_ipca2())
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
                next_url = request.GET.get('next')
                if next_url and next_url != reverse('login_view'):
                    return redirect(next_url)
                else:
                    return redirect('home')
            else:
                form.add_error(None,"Invalid credentials")
    else:
        form = LoginForm()
    return render(request,'home/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

def signup(request): 
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login_view')
    else:
        form = SignUpForm()

    return render(request,'home/signup.html', {'form':form})

@login_required
def investments(request):
    asset_list = Asset.objects.all()
    if request.method == 'POST':
        form = NewAssetForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('investments')
    else:
        form = NewAssetForm()
    return render(request,'home/investments.html',{'asset_list':asset_list,'form':form})

def delete_asset(request,item_id):
    asset = get_object_or_404(Asset,id=item_id)
    asset.delete()
    return redirect('investments')