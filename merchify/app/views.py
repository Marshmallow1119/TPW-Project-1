from datetime import timedelta
from django.utils import timezone
from django.shortcuts import redirect, render, get_object_or_404
from django.shortcuts import render
from app.models import *
from app.forms import RegisterForm
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import logout as auth_logout
from .forms import RegisterForm
from django.contrib.auth.models import User

def home(request):
    artists = Artist.objects.all()  
    one_week_ago = timezone.now() - timedelta(weeks=1)
    recent_products = Product.objects.filter(addedProduct__gte=one_week_ago)
    if request.user.is_authenticated:
        return render(request, 'home_login.html', {'artists': artists,'products':recent_products})
    return render(request, 'home.html', {'artists': artists,'products':recent_products})

def produtos(request):
    return render(request, 'produtos.html')

def artistas(request):
    artists = Artist.objects.all()
    for artist in artists:
        print(artist.image)
    return render(request, 'artistas.html', {'artists': artists})


def artistsProducts(request, name):
    artist = get_object_or_404(Artist, name=name)
    products = Product.objects.filter(artist=artist)
    return render(request, 'artists_products.html', {'artist': artist, 'products': products})

def productDetails(request, identifier):
    product = get_object_or_404(Product, id=identifier)
    if isinstance(product, Vinil) or isinstance(product, CD):
        return render(request, 'productDetailsVinil.html', {'product': product})
    return render(request, 'productDetails.html', {'product': product})

def register(request):
    print("A view 'register' foi chamada.") 

    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)

        if form.is_valid():

            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            raw_password = form.cleaned_data['password1']

            if User.objects.filter(username=username).exists():
                return render(request, 'register_user.html', {'form': form, 'error': "Usuário já existe."})

            user = User.objects.create_user(username=username, email=email, password=raw_password)
            user.save()

            auth_login(request, user)

            return redirect('login') 
        else:
            return render(request, 'register_user.html', {'form': form, 'error': "Formulário inválido. Verifique os campos."})
    else:
        form = RegisterForm()
        return render(request, 'register_user.html', {'form': form})
    

def login(request):  

    if request.method == 'POST':
        
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not User.objects.filter(username=username).exists():
            error_message = "Username does not exist"
            return render(request, 'login.html', {'error_message': error_message})
        
       
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)  
            return redirect('home_login')
        else:
            error_message = "Invalid username or password"
            return render(request, 'login.html', {'error_message': error_message})
    else:
        return render(request, 'login.html')


def logout(request):
    if request.user.is_authenticated:
        auth_logout(request)  
    return redirect('home') 
