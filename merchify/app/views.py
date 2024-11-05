from datetime import timedelta, date
import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.http import JsonResponse
from django.utils import timezone
from django.shortcuts import redirect, render, get_object_or_404
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from app.models import *
from app.forms import RegisterForm
from django.contrib.auth import authenticate, login as auth_login, get_user_model
from django.contrib.auth import logout as auth_logout
from .forms import RegisterForm
from django.contrib.auth.models import User

User = get_user_model()


def home(request):
    artists = Artist.objects.all()  
    one_week_ago = timezone.now() - timedelta(weeks=1)  # Corrigido para filtrar por uma semana atrás
    recent_products = Product.objects.filter(addedProduct__gte=one_week_ago).order_by('-addedProduct')
    
    return render(request, 'home.html', {'artists': artists, 'products': recent_products})


def produtos(request):
    produtos= Product.objects.all()
    sort= request.GET.get('sort', 'featured')
    if sort == 'priceAsc':
        produtos = produtos.order_by('price')
    elif sort == 'priceDesc':
        produtos = produtos.order_by('-price')
    return render(request, 'products.html', {'produtos': produtos})

def artistas(request):
    artists = Artist.objects.all()
    for artist in artists:
        print(artist.image)
    return render(request, 'artistas.html', {'artists': artists})


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
    average_rating = product.reviews.aggregate(Avg('rating'))['rating__avg'] or 0  # Default to 0 if no reviews
    return render(request, 'productDetails.html', {'product': product, 'average_rating': average_rating})

def search_products(request):
    query = request.GET.get('search', '')  # Get the search term from the query string
    products = Product.objects.filter(name__icontains=query) if query else Product.objects.none()  # Filter products if a query exists
    return render(request, 'search_results.html', {'products': products, 'query': query})


def register(request):
    print("A view 'register' foi chamada.")

    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)

        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            raw_password = form.cleaned_data['password1']

            # Check if the user already exists
            if User.objects.filter(username=username).exists():
                return render(request, 'register_user.html', {'form': form, 'error': "Usuário já existe."})

            # Create the user
            user = User.objects.create_user(username=username, email=email, password=raw_password)
            user.save()

            # Automatically log in the user after registration
            auth_login(request, user)

            return redirect('login')  # Adjust this redirect according to your URL names
        else:
            return render(request, 'register_user.html',
                          {'form': form, 'error': "Formulário inválido. Verifique os campos."})
    else:
        form = RegisterForm()
        return render(request, 'register_user.html', {'form': form})


def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Check if the user exists
        if not User.objects.filter(username=username).exists():
            error_message = "Username does not exist"
            return render(request, 'login.html', {'error_message': error_message})

        # Authenticate the user
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('home')  # Adjust this redirect according to your URL names
        else:
            error_message = "Invalid username or password"
            return render(request, 'login.html', {'error_message': error_message})
    else:
        return render(request, 'login.html')
@login_required
def logout(request):
    if request.user.is_authenticated:
        auth_logout(request)  
    return redirect('home') 

@login_required
@csrf_exempt  # This decorator is needed if CSRF token is not provided in request headers.
def add_to_cart(request, product_id):
    if request.method == "POST":
        try:
            if not isinstance(request.user, User):
                return JsonResponse({"error": "User is not authenticated."}, status=400)
            data = json.loads(request.body)
            quantity = int(data.get("quantity", 1))
            size_id = data.get("size")

            product = get_object_or_404(Product, id=product_id)
            
            cart, created = Cart.objects.get_or_create(user=request.user, defaults={"date": date.today(), "total": 0.0})

            cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product, defaults={"quantity": quantity, "total": product.price * quantity})

            if not item_created:
                cart_item.quantity += quantity
                cart_item.total += product.price * quantity
                cart_item.save()

            cart.total += product.price * quantity
            cart.save()

            return JsonResponse({"message": "Produto adicionado ao carrinho!"})

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)

    return JsonResponse({"error": "Invalid request"}, status=400)

@login_required
def viewCart(request):
    user = request.user
    try:
        cart = Cart.objects.get(user=user)  # Use get() to retrieve a single cart
    except Cart.DoesNotExist:
        return redirect('store')  # Redirect to store if cart doesn't exist

    cartitems = CartItem.objects.filter(cart=cart)
    context = {
        'cart_items': cartitems,  # Use 'cart_items' as key in context
    }
    return render(request, 'cart.html', context)

@login_required
def update_cart_item(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        quantity = int(request.POST.get('quantity'))

        cart_item = get_object_or_404(CartItem, id=item_id)
        cart_item.quantity = quantity
        cart_item.save()

        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False})

@login_required
def remove_from_cart(request, product_id):
    cart_item = get_object_or_404(CartItem, id=product_id)
    cart_item.delete()



@login_required
def profile(request):
    user = request.user
    purchases = Purchase.objects.filter(user=user)
    
    # Calcula o número de compras
    number_of_purchases = purchases.count()

    # Atualiza o contexto com o número de compras
    context = {
        'purchases': purchases,
        'profile_picture': user.profile_picture.url if user.profile_picture else None,
        'number_of_purchases': number_of_purchases,
    }
    
    return render(request, 'profile.html', context)


@login_required
def submit_review(request, product_id):
    if request.method == "POST":
        # Get the rating and review text from the form data
        rating = request.POST.get("rating")
        review_text = request.POST.get("review")
        product = get_object_or_404(Product, id=product_id)

        # Validate the rating
        if rating and review_text:
            try:
                rating = int(rating)
                if not 1 <= rating <= 5:
                    messages.error(request, "Rating must be between 1 and 5.")
                    return redirect("productDetails", identifier=product_id)
            except ValueError:
                messages.error(request, "Invalid rating.")
                return redirect("productDetails", identifier=product_id)

            # Save the review with the current date
            Review.objects.create(
                product=product,
                user=request.user,
                rating=rating,
                text=review_text,
                date=timezone.now().date()  # Set the current date
            )
            messages.success(request, "Your review has been submitted.")
        else:
            messages.error(request, "Please provide both a rating and a review.")

        # Redirect back to the product page
        return redirect("productDetails", identifier=product_id)