from django.shortcuts import redirect, render, get_object_or_404
from django.shortcuts import render
from app.models import *
from app.forms import RegisterForm
from django.contrib.auth import authenticate, login as auth_login

def home(request):
    artists = Artist.objects.all()  
    return render(request, 'home.html', {'artists': artists})

def produtos(request):
    return render(request, 'produtos.html')

def artistas(request):
    artists = Artist.objects.all()
    for artist in artists:
        print(artist.image)
    return render(request, 'artistas.html', {'artists': artists})

def login(request):
    return render(request, 'login.html')

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
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        print(form.errors)

        if form.is_valid():
            # Check if user already exists
            u = User.objects.filter(username=form.cleaned_data['username'])

            if u:
                return render(request, 'register.html', {'form': form, 'error': True})

            else:
                form.save()
                email = form.cleaned_data.get('email')
                username = form.cleaned_data.get('username')
                raw_password = form.cleaned_data.get('password1')

                # Authenticate user then login
                user = authenticate(username=username, password=raw_password)
                auth_login(request, user)

                # Create user in our database
                user = User.objects.create(username=username, email=email, password=raw_password,
                                           name=form.cleaned_data['name'])
                user.save()

                return redirect('/')
        else:
            return render(request, 'register.html', {'form': form, 'error': True})
    else:
        form = RegisterForm()
        return render(request, 'register.html', {'form': form, 'error': False})