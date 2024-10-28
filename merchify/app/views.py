from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.shortcuts import render

from app.models import Artist, Product


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

