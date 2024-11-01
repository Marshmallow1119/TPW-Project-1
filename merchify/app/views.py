from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.shortcuts import render

from app.models import Artist, Product, Vinil, CD


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
    sort = request.GET.get('sort', 'featured')  # Default to 'featured' sorting

    # Define sorting logic based on the 'sort' parameter
    if sort == 'priceAsc':
        products = products.order_by('price')  # Ascending price
    elif sort == 'priceDesc':
        products = products.order_by('-price')  # Descending price
    return render(request, 'artists_products.html', {'artist': artist, 'products': products})

def productDetails(request, identifier):
    product = get_object_or_404(Product, id=identifier)
    if isinstance(product, Vinil) or isinstance(product, CD):
        return render(request, 'productDetailsVinil.html', {'product': product})
    return render(request, 'productDetails.html', {'product': product})

def search_products(request):
    query = request.GET.get('search', '')  # Get the search term from the query string
    products = Product.objects.filter(name__icontains=query) if query else Product.objects.none()  # Filter products if a query exists
    return render(request, 'search_results.html', {'products': products, 'query': query})

