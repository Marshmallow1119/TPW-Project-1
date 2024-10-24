from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

from app.models import Artist


def home(request):
    return render(request, 'home.html')

def produtos(request):
    return render(request, 'produtos.html')

def artistas(request):
    artists = Artist.objects.all()
    for artist in artists:
        print(artist.image)
    return render(request, 'artistas.html', {'artists': artists})

