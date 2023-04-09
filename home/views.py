from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.gis.geoip2 import GeoIP2
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.cache import cache_page
from geoip2.errors import AddressNotFoundError
from django.http import JsonResponse

from .forms import LoginForm, NewAssetForm, SignUpForm
from .models import Asset
from .utils import (get_btc, get_dolar, get_home_api_calls, get_fundamentals,
                    get_highest_volume_stocks, get_historic_prices, get_ipca2,
                    get_selic, get_weather)


@cache_page(7200)
def home(request):

    context = get_home_api_calls(request)

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
                    context = get_home_api_calls(request)
                    context.update({'user':user})
                    return render(request,'home/index.html',context)
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

@login_required
def consult_investments(request,item_id):
    if request.method == 'GET':
        asset = get_object_or_404(Asset,id=item_id)
        asset_data = {
            'symbol': asset.symbol,
            'amount': asset.amount,
            'price': asset.price,
            'operation': asset.operation,
            'operation_date': asset.operation_date,
            'created_date': asset.created_date,
            'updated_date': asset.updated_date,
        }
    return JsonResponse(asset_data)

def delete_asset(request,item_id):
    asset = get_object_or_404(Asset,id=item_id)
    asset.delete()
    return redirect('investments')