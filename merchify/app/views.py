from datetime import timedelta, date
import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.http import JsonResponse, Http404
from django.utils import timezone
from django.shortcuts import redirect, render, get_object_or_404
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError

from app.models import *
from app.forms import RegisterForm, ProductForm
from django.contrib.auth import authenticate, login as auth_login, get_user_model
from django.contrib.auth import logout as auth_logout
from .forms import RegisterForm, UploadUserProfilePicture, UpdatePassword, UpdateProfile
from django.contrib.auth.models import User


User = get_user_model()


def home(request):
    artists = Artist.objects.all()
    recent_products = Product.objects.order_by('-addedProduct')[:20]  # Limita a 20 produtos mais recentes

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

    if request.user.is_authenticated:
        favorited_product_ids = Favorite.objects.filter(user=request.user).values_list('product_id', flat=True)
    else:
        favorited_product_ids = []  # Empty list if user is not authenticated

        # Add a new property to each product indicating if it is favorited by the user
    for product in products:
            product.is_favorited = product.id in favorited_product_ids
    return render(request, 'artists_products.html', {'artist': artist, 'products': products})


from django.shortcuts import render, get_object_or_404
from django.db.models import Avg
from .models import Product, Clothing, CD, Vinil


def productDetails(request, identifier):
    product = get_object_or_404(Product, id=identifier)

    context = {
        'product': product,
    }

    if isinstance(product, Clothing):
        sizes = product.sizes.all()  # Get all sizes related to the clothing item
        context['sizes'] = sizes  # Add sizes to context

    average_rating = product.reviews.aggregate(Avg('rating'))['rating__avg'] or 0  # Default to 0 if no reviews
    context['average_rating'] = average_rating  # Add average rating to context
    print(isinstance(product, Clothing))

    return render(request, 'productDetails.html', context)


def search_products(request):
    query = request.GET.get('search', '')  # Get the search term from the query string
    products = Product.objects.filter(name__icontains=query) if query else Product.objects.none()  # Filter products if a query exists
    return render(request, 'search_results.html', {'products': products, 'query': query})




def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES) 
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']
            address = form.cleaned_data['address']
            country = form.cleaned_data['country']
            raw_password = form.cleaned_data['password1']
            image = form.cleaned_data['image']
            

            if User.objects.filter(username=username).exists():
                messages.error(request, "Usuário já existe.")
                return render(request, 'register_user.html', {'form': form})

            user = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                phone=phone,
                address=address,
                country=country,
                password=raw_password,
                image=image
            )
            user.save()

            auth_login(request, user)

            messages.success(request, "Registro realizado com sucesso! Você está agora logado.")
            return redirect('home')
        else:
            messages.error(request, "Formulário inválido. Verifique os campos.")
            return render(request, 'register_user.html', {'form': form})
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
            
            cart, created = Cart.objects.get_or_create(user=request.user, defaults={"date": date.today()})

            cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product, defaults={"quantity": quantity})

            if not item_created:
                cart_item.quantity += quantity
                cart_item.save()

            cart.save()

            return JsonResponse({"message": "Produto adicionado ao carrinho!"})

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)

    return JsonResponse({"error": "Invalid request"}, status=400)

@login_required
def viewCart(request):
    user = request.user
    try:
        cart = Cart.objects.get(user=user)
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
    try:
        cart_item = CartItem.objects.get(product_id=product_id)
        cart_item.delete()
    except CartItem.DoesNotExist:
        raise Http404("CartItem does not exist")
    return redirect('cart')
import logging
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from .forms import UploadUserProfilePicture, UpdateProfile, UpdatePassword
from .models import Purchase

# Configuração básica do logger
logger = logging.getLogger(__name__)

@login_required(login_url='/login')
def profile(request):
    user = request.user

    if request.method == 'GET':
        logger.debug("Método GET acionado, carregando formulário.")
        image_form = UploadUserProfilePicture()
        profile_form = UpdateProfile(initial={
            'name': user.first_name,
            'surname': user.last_name,
            'email': user.email,
            'username': user.username,
            'address': user.address,
            'phone': user.phone,
            'country': user.country
        })
        password_form = UpdatePassword()
        purchases = Purchase.objects.filter(user=user)

        return render(request, 'profile.html', {
            'user': user,
            'image_form': image_form,
            'profile_form': profile_form,
            'password_form': password_form,
            'number_of_purchases': purchases.count(),
            'purchases': purchases,
        })

    elif request.method == 'POST':
        if 'save' in request.POST:
            logger.debug("Salvando alterações no perfil do usuário.")
            user.first_name = request.POST.get('name', user.first_name)
            user.last_name = request.POST.get('surname', user.last_name)
            user.email = request.POST.get('email', user.email)
            user.username = request.POST.get('username', user.username)
            user.address = request.POST.get('address', user.address)
            user.phone = request.POST.get('phone', user.phone)
            user.country = request.POST.get('country', user.country)
            
            if 'image' in request.FILES:
                logger.debug("Imagem de perfil recebida.")
                user.image = request.FILES['image']

            user.save()
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('/account/profile')

        elif 'delete_account' in request.POST:
            logger.debug("Solicitação para eliminar a conta recebida.")
            user.delete()
            messages.success(request, 'Conta eliminada com sucesso!')
            return redirect('/login')

        elif 'submit_password' in request.POST:
            logger.debug("Solicitação para mudar a senha recebida.")
            old_password = request.POST.get('old_password')
            new_password = request.POST.get('new_password')
            confirm_new_password = request.POST.get('confirm_new_password')

            # Verificar se todos os campos de senha estão preenchidos
            if not old_password or not new_password or not confirm_new_password:
                logger.warning("Campos de senha não preenchidos.")
                messages.error(request, 'Todos os campos de senha são obrigatórios.')
            else:
                if user.check_password(old_password):
                    logger.debug("Senha antiga correta.")
                    if new_password == confirm_new_password:
                        logger.debug("Novas senhas coincidem.")
                        try:
                            # Validar a nova senha
                            password_validation.validate_password(new_password, user)
                            logger.debug("Nova senha válida.")
                            user.set_password(new_password)
                            user.save()
                            messages.success(request, 'Senha alterada com sucesso!')
                            return redirect('/account/profile')
                        except ValidationError as e:
                            logger.error("Erro de validação de senha: %s", e)
                            for error in e.messages:
                                messages.error(request, error)
                    else:
                        logger.warning("As novas senhas não coincidem.")
                        messages.error(request, 'As senhas não coincidem!')
                else:
                    logger.warning("Senha antiga incorreta.")
                    messages.error(request, 'Senha antiga incorreta!')

    logger.debug("Carregando informações do usuário para a renderização.")
    purchases = Purchase.objects.filter(user=user)
    return render(request, 'profile.html', {
        'user': user,
        'number_of_purchases': purchases.count(),
        'purchases': purchases,
    })


@login_required
def submit_review(request, product_id):
    if request.method == "POST":
        rating = request.POST.get("rating")
        review_text = request.POST.get("review")
        product = get_object_or_404(Product, id=product_id)

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
    
@login_required
def checkfavorite(request):
    favorite_products = Favorite.objects.filter(user=request.user).select_related('product')
    products_list = [{'id': fav.product.id, 'name': fav.product.name, 'price': fav.product.price, 'image': fav.product.image.url} for fav in favorite_products]
    return render(request, "favorites.html", {"favorite_products": products_list})


@require_POST
@login_required  # Ensure the user is logged in
def addtofavorite(request, product_id):
    try:
        # Fetch the product and user
        product = Product.objects.get(id=product_id)
        user = request.user

        # Check if this product is already a favorite
        favorite, created = Favorite.objects.get_or_create(user=user, product=product)

        if created:
            # Product was added to favorites
            favorited = True
        else:
            favorite.delete()
            favorited = False

        return JsonResponse({"success": True, "favorited": favorited})

    except Product.DoesNotExist:
        # Handle case if product does not exist
        return JsonResponse({"success": False, "message": "Product not found."}, status=404)
    except Exception as e:
        # Handle any other unexpected errors
        return JsonResponse({"success": False, "message": str(e)}, status=500)

@login_required
def remove_from_favorites(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        user = request.user
        Favorite.objects.filter(user=user, product=product).delete()
        return redirect( 'favorites')
    except Product.DoesNotExist:
        return JsonResponse({"success": False, "message": "Product not found."}, status=404)


@login_required
def payment(request):
    user = request.user
    cart = Cart.objects.get(user=user)
    cart_items = CartItem.objects.filter(cart=cart)
    total = cart.total
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        shipping_address = request.POST.get('shipping_address')
        purchase = Purchase.objects.create(
            user=user,
            date=timezone.now().date(),
            total=total,
            paymentMethod=payment_method,
            shippingAddress=shipping_address,
            status='Processing'
        )
        purchase.products.set([item.product for item in cart_items])
        cart_items.delete()
        cart.delete()
        return redirect('home')
    return render(request, 'payment.html', {"carrinho":cart_items,'total': total})




#@login_required
def supplier_product_list(request):
    # Dados de exemplo para testar o layout da página
    products = [
        {
            "name": "Produto Exemplo 1",
            "price": 20.0,
            "image": {"url": "https://via.placeholder.com/250"},
            "artist": {"image": {"url": "https://via.placeholder.com/100"}},
        },
        {
            "name": "Produto Exemplo 2",
            "price": 35.0,
            "image": {"url": "https://via.placeholder.com/250"},
            "artist": {"image": {"url": "https://via.placeholder.com/100"}},
        },
    ]

    return render(request, 'supplier/product_list.html', {'products': products})


def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.company = request.user.supplier_profile.company
            product.save()
            return redirect('supplier_product_list')
    else:
        form = ProductForm()

    return render(request, 'supplier/product_form.html', {'form': form, 'is_edit': False})

def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, company=request.user.supplier_profile.company)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('supplier_product_list')
    else:
        form = ProductForm(instance=product)

    return render(request, 'supplier/product_form.html', {'form': form, 'is_edit': True, 'product': product})


def company_products(request, company_id):
    # Obter a empresa específica usando o ID
    company = get_object_or_404(Company, id=company_id)

    # Obter todos os produtos associados a esta empresa
    products = company.products.all()  # Utiliza o related_name definido no modelo Product

    # Renderizar o template com os produtos da empresa
    return render(request, 'company_products.html', {'company': company, 'products': products})

#@login_required
def add_product_to_company(request, company_id):
    company = get_object_or_404(Company, id=company_id)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.company = company
            product.save()
            return redirect('company_products', company_id=company.id)
    else:
        form = ProductForm()

    return render(request, 'add_product_to_company.html', {'form': form, 'company': company})


def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('company_products', company_id=product.company.id)
    else:
        form = ProductForm(instance=product)

    return render(request, 'edit_product.html', {'form': form, 'product': product})

#@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    company_id = product.company.id  # Guarda o ID da empresa para redirecionamento
    product.delete()
    return redirect('company_products', company_id=company_id)
