from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

def home(request):
    return render(request, 'home.html')

def produtos(request):
    return render(request, 'produtos.html')

def artistas(request):
    return render(request, 'artistas.html')

