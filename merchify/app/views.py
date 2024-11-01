from datetime import timedelta
from django.utils import timezone
from django.shortcuts import redirect, render, get_object_or_404
from django.shortcuts import render
from app.models import *
from app.forms import RegisterForm
from django.contrib.auth import authenticate, login as auth_login

def home(request):
    artists = Artist.objects.all()  
    one_week_ago = timezone.now() - timedelta(weeks=1)
    recent_products = Product.objects.filter(addedProduct__gte=one_week_ago)
    return render(request, 'home.html', {'artists': artists,'products':recent_products})

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
            # Verifica se o usuário já existe
            username = form.cleaned_data['username']
            if User.objects.filter(username=username).exists():
                return render(request, 'register_user.html', {'form': form, 'error': True})

            # Cria o usuário com a senha criptografada
            email = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password1')
            profile_picture = form.cleaned_data.get('profile_picture')

            user = User.objects.create(username=username, email=email, password=raw_password)
            user.set_password(raw_password)
            user.numberOfPurchases=0
            if profile_picture:
                user.profile_pictures = profile_picture
            user.save()

            # Autentica e faz login do usuário
            user = authenticate(username=username, password=raw_password)

            if user is not None:
                auth_login(request, user)

            return redirect('/')
        else:
            # Renderiza o formulário com erros se houver campos inválidos
            return render(request, 'register_user.html', {'form': form, 'error': True})
    else:
        # Renderiza o formulário vazio para requisição GET
        form = RegisterForm()
        return render(request, 'register_user.html', {'form': form, 'error': False})