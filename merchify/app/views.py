from datetime import timedelta, date
import json
import logging
from itertools import product

import re
from urllib.parse import urlencode
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.db.models import Avg, Count
from django.http import JsonResponse, Http404
from django.urls import reverse
from django.utils import timezone
from django.shortcuts import redirect, render, get_object_or_404
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError

from app.models import *
from app.forms import RegisterForm, ProductForm, CompanyForm, UserForm, VinilForm, CDForm, ClothingForm, AccessoryForm
from django.contrib.auth import authenticate, login as auth_login, get_user_model
from django.contrib.auth import logout as auth_logout
from .forms import RegisterForm, UploadUserProfilePicture, UpdatePassword, UpdateProfile
from django.contrib.auth.models import User
from django.db import transaction


User = get_user_model()


def home(request):
    artists = Artist.objects.all()
    recent_products = Product.objects.order_by('-addedProduct')[:20]

    if request.session.get('clear_cart'):
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            cart.items.all().delete()
            cart.delete()

        del request.session['clear_cart']

    user = request.user
    show_promotion= False

    if user.is_authenticated:
        if user.user_type == 'admin':
            return redirect('admin_home')
        elif user.user_type == 'company':
             return redirect('company_products',user.company.id)
        show_promotion= not Purchase.objects.filter(user=user).exists()
    else:
        show_promotion= True

    recently_viewed_ids = request.session.get('recently_viewed', [])
    recently_viewed_products = Product.objects.filter(id__in=recently_viewed_ids)
    recently_viewed_products = sorted(
        recently_viewed_products,
        key=lambda product: recently_viewed_ids.index(product.id)
    )
        

    return render(request, 'home.html', {'artists': artists, 'products': recent_products, 'show_promotion': show_promotion, 'recently_viewed_products': recently_viewed_products})

# def home(request):
#     return render(request, 'home.html')

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
    
    sort = request.GET.get('sort', 'featured')
    if sort == 'priceAsc':
        products = products.order_by('price')
    elif sort == 'priceDesc':
        products = products.order_by('-price')

    if request.user.is_authenticated:
        favorited_product_ids = Favorite.objects.filter(user=request.user).values_list('product_id', flat=True)
    else:
        favorited_product_ids = []

    for product in products:
        product.is_favorited = product.id in favorited_product_ids


    background_url = artist.background_image.url


    context = {
        'artist': artist,
        'products': products,
        'background_url': background_url,
    }

    return render(request, 'artists_products.html', context)


def productDetails(request, identifier):
    product = get_object_or_404(Product, id=identifier)
    product.count = product.count + 1
    product.save()

    recently_viewed = request.session.get('recently_viewed', [])
    if product.id in recently_viewed:
        recently_viewed.remove(product.id)
    recently_viewed.insert(0, product.id)
    recently_viewed = recently_viewed[:4]
    request.session['recently_viewed'] = recently_viewed

    context = {
        'product': product,
    }

    if isinstance(product, Clothing):
        sizes = product.sizes.all() 
        context['sizes'] = sizes 

    average_rating = product.reviews.aggregate(Avg('rating'))['rating__avg'] or 0 
    context['average_rating'] = average_rating  
    print(isinstance(product, Clothing))

    return render(request, 'productDetails.html', context)


def search_products(request):
    query = request.GET.get('search', '')
    products = Product.objects.filter(name__icontains=query) if query else Product.objects.none()
    if query == '':
        products = Product.objects.all()
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

        if not User.objects.filter(username=username).exists():
            error_message = "Username does not exist"
            return render(request, 'login.html', {'error_message': error_message})

        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            if hasattr(user, 'user_type'):
                if user.user_type == 'individual':
                    return redirect('home')
                elif user.user_type == 'company':
                    company_id = user.company.id
                    return redirect('company_products', company_id=company_id)
                elif user.user_type == 'admin':
                    return redirect('admin_home')
                else:
                    return redirect('home')
            else:
                return redirect('home')
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
@csrf_exempt  
def add_to_cart(request, product_id):
    if request.method == "POST":
        try:
            if not isinstance(request.user, User):
                return JsonResponse({"error": "User is not authenticated."}, status=400)
            
            data = json.loads(request.body)
            quantity = int(data.get("quantity", 1))
            size_id = data.get("size") 

            product = get_object_or_404(Product, id=product_id)
            
            size = None
            if product.get_product_type() == 'Clothing':
                if not size_id:
                    return JsonResponse({"error": "Size is required for clothing items."}, status=400)
                size = get_object_or_404(Size, id=size_id)
            
            cart, created = Cart.objects.get_or_create(user=request.user, defaults={"date": date.today()})
            
            cart_item, item_created = CartItem.objects.get_or_create(
                cart=cart, 
                product=product, 
                size=size,  
                defaults={"quantity": quantity}
            )

            if not item_created:
                cart_item.quantity += quantity
                cart_item.save()

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
        cart = Cart.objects.create(user=user)

    cartitems = CartItem.objects.filter(cart=cart)
    context = {
        'cart_items': cartitems, 
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
        cart = Cart.objects.get(user=request.user)
        cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
        cart_item.delete()
    except CartItem.DoesNotExist:
        raise Http404("CartItem does not exist")
    return redirect('cart')




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
            phone = request.POST.get('phone', user.phone)
            user.country = request.POST.get('country', user.country)

            if not re.fullmatch(r'\d{9}', phone):
                messages.error(request, 'O número de telefone deve conter exatamente 9 dígitos.')
                profile_form = UpdateProfile(initial={
                    'name': user.first_name,
                    'surname': user.last_name,
                    'email': user.email,
                    'username': user.username,
                    'address': user.address,
                    'phone': phone, 
                    'country': user.country
                })
                image_form = UploadUserProfilePicture()
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
            else:
                user.phone = phone
            
            if 'image' in request.FILES:
                logger.debug("Imagem de perfil recebida.")
                user.image = request.FILES['image']

            user.save()
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('/account/profile')

        elif 'delete_account' in request.POST:
            logger.debug("Solicitação para eliminar a conta recebida.")
            user.delete()
            return redirect('home')

        elif 'submit_password' in request.POST:
            logger.debug("Solicitação para mudar a senha recebida.")
            old_password = request.POST.get('old_password')
            new_password = request.POST.get('new_password')
            confirm_new_password = request.POST.get('confirm_new_password')

            if not old_password or not new_password or not confirm_new_password:
                logger.warning("Campos de senha não preenchidos.")
                messages.error(request, 'Todos os campos de senha são obrigatórios.')
            else:
                if user.check_password(old_password):
                    logger.debug("Senha antiga correta.")
                    if new_password == confirm_new_password:
                        logger.debug("Novas senhas coincidem.")
                        try:
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

            Review.objects.create(
                product=product,
                user=request.user,
                rating=rating,
                text=review_text,
                date=timezone.now().date() 
            )
            messages.success(request, "Your review has been submitted.")
        else:
            messages.error(request, "Please provide both a rating and a review.")

        return redirect("productDetails", identifier=product_id)
    
@login_required
def checkfavorite(request):
    favorite_products = Favorite.objects.filter(user=request.user).select_related('product')
    products_list = [{'id': fav.product.id, 'name': fav.product.name, 'price': fav.product.price, 'image': fav.product.image.url} for fav in favorite_products]
    return render(request, "favorites.html", {"favorite_products": products_list})


@require_POST
@login_required(login_url='/login/')
def addtofavorite(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        user = request.user

        favorite, created = Favorite.objects.get_or_create(user=user, product=product)

        if created:
            favorited = True
        else:
            favorite.delete()
            favorited = False

        return JsonResponse({"success": True, "favorited": favorited})

    except Product.DoesNotExist:
        return JsonResponse({"success": False, "message": "Product not found."}, status=404)
    except Exception as e:
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
def process_payment(request):
    if request.method == 'POST' and 'complete_payment' in request.POST:
        user = request.user
        try:
            cart = Cart.objects.get(user=user)
            cart_items = CartItem.objects.filter(cart=cart)

            payment_method = request.POST.get('payment_method')
            shipping_address = request.POST.get('shipping_address')
            discount_code = request.POST.get('discount_code')

            if not payment_method or not shipping_address:
                messages.error(request, "Por favor, preencha todos os campos obrigatórios.")
                return redirect('payment_page')

            total = cart.total
            discount_applied = False
            discount_value = 0

            if discount_code and discount_code.lower() == 'primeiracompra':
                if not Purchase.objects.filter(user=user).exists():
                    discount_applied = True
                    discount_value = total * 0.10 
                    total -= discount_value  
                    request.session['discount_applied'] = True
                    messages.success(request, "Código de desconto aplicado com sucesso!")
                else:
                    messages.warning(request, "O código de desconto só é válido para a primeira compra.")
                    request.session['discount_applied'] = False

            shipping_cost = request.session.get('shipping_cost', 0)
            final_total = total + shipping_cost

            with transaction.atomic():
                purchase = Purchase.objects.create(
                    user=user,
                    date=timezone.now().date(),
                    paymentMethod=payment_method,
                    shippingAddress=shipping_address,
                    total_amount=final_total,
                    status='Processing'
                )

                for item in cart_items:
                    product = item.product
                    product_type = product.get_product_type()
                    stock_available = product.get_stock()

                    if stock_available is not None and stock_available >= item.quantity:
                        if isinstance(product, (Vinil, CD, Accessory)):
                            product.stock -= item.quantity
                            product.save()
                        elif isinstance(product, Clothing) and item.size:
                            size = item.size
                            if size.stock >= item.quantity:
                                size.stock -= item.quantity
                                size.save()
                            else:
                                messages.error(request, f"Estoque insuficiente para {product.name} no tamanho {size.size}. Disponível: {size.stock}")
                                return redirect('payment_page')
                    else:
                        messages.error(request, f"Estoque insuficiente para {product.name}. Disponível: {stock_available}")
                        return redirect('payment_page')

                    PurchaseProduct.objects.create(
                        purchase=purchase,
                        product=product,
                        quantity=item.quantity
                    )

                request.session['clear_cart'] = True
                request.session['discount_applied'] = False
                url_with_success = f"{reverse('payment_page')}?success=1"
                return redirect(url_with_success)

        except Cart.DoesNotExist:
            messages.error(request, "Carrinho não encontrado.")
            return redirect('cart')
        except Exception as e:
            messages.error(request, f"Ocorreu um erro durante o processamento do pagamento: {str(e)}")
            return redirect('payment_page')

    return redirect('payment_page')


@login_required
def payment_confirmation(request):
    return render(request, 'payment_confirmation.html')

@login_required
def payment_page(request):
    user = request.user
    cart = Cart.objects.get(user=user)
    cart_items = CartItem.objects.filter(cart=cart)
    subtotal = cart.total

    discount_value = 0

    discount_applied = request.session.get('discount_applied', False)
    if discount_applied:
        discount_value = subtotal * 0.10 
        

    shipping_cost = 0
    if subtotal <= 100:
        if user.country == 'Portugal':
            shipping_cost = 4.99
        else:
            shipping_cost = 6.00

    request.session['shipping_cost'] = shipping_cost

    final_total = subtotal - discount_value + shipping_cost

    return render(request, 'payment.html', {
        "cart_items": cart_items,
        "subtotal": subtotal,
        "shipping_cost": shipping_cost,
        "final_total": final_total,
        "discount_value": discount_value,
        "discount_applied": discount_applied
    })

@login_required
def company_home(request):
    company_id = request.user.company.id if request.user.user_type == 'company' else None
    print("Company ID:", company_id)
    return render(request, 'company_home.html', {'company_id': company_id})

@login_required
def company_products(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    products = company.products.prefetch_related('favorites', 'reviews')  

    for product in products:
        product.favorites_count = product.favorites.count()  
        product.reviews_count = product.reviews.count()      

    return render(request, 'company_products.html', {'company': company, 'products': products})

@login_required
def company_product_detail(request, company_id, product_id):
    company = get_object_or_404(Company, id=company_id)
    product = get_object_or_404(Product, id=product_id, company=company)

    product.favorites_count = product.favorites.count()
    reviews = product.reviews.all()

    return render(request, 'company_product_detail.html', {
        'company': company,
        'product': product,
        'reviews': reviews,
    })

@login_required
def add_product_to_company(request, company_id):
    company = Company.objects.get(id=company_id)
    if request.method == 'POST':
        product_form = ProductForm(request.POST, request.FILES)
        if product_form.is_valid():
            product = product_form.save(commit=False)
            product.company = company  # Set company
            product.save()

            # Save additional fields based on product type
            product_type = product_form.cleaned_data['product_type']
            if product_type == 'vinil':
                vinil_form = VinilForm(request.POST, instance=product, required=False)
                if vinil_form.is_valid():
                    vinil_form.save()
            elif product_type == 'cd':
                cd_form = CDForm(request.POST, instance=product, required=False)
                if cd_form.is_valid():
                    cd_form.save()
            elif product_type == 'clothing':
                clothing_form = ClothingForm(request.POST, instance=product, required=False)
                if clothing_form.is_valid():
                    clothing_form.save()
            elif product_type == 'accessory':
                accessory_form = AccessoryForm(request.POST, instance=product, required=False)
                if accessory_form.is_valid():
                    accessory_form.save()

            return redirect('company_products', company_id=company.id)

    else:
        product_form = ProductForm()
        vinil_form = VinilForm()
        cd_form = CDForm()
        clothing_form = ClothingForm()
        accessory_form = AccessoryForm()

    context = {
        'company': company,
        'form': product_form,
        'vinil_form': vinil_form,
        'cd_form': cd_form,
        'clothing_form': clothing_form,
        'accessory_form': accessory_form,
    }
    return render(request, 'add_product_to_company.html', context)

@login_required
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

@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    company_id = product.company.id  # Guarda o ID da empresa para redirecionamento
    product.delete()
    return redirect('company_products', company_id=company_id)

def admin_home(request):
    users = User.objects.all()
    products = Product.objects.all()
    for product in products:
        product.review_count = Review.objects.filter(product=product).count()  # Count reviews for this product
    return render(request, 'admin_home.html', {'users': users, 'products': products})
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    return redirect('admin_home')
def admin_product_delete(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return redirect('admin_home')

@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    product = review.product
    company = product.company

    # Verifica se o utilizador é administrador ou proprietário da companhia do produto
    if request.user.user_type == 'admin' or (request.user.user_type == 'company' and request.user.company == company):
        review.delete()
        messages.success(request, "Avaliação removida com sucesso.")
        return redirect('company_product_detail', company_id=company.id, product_id=product.id)
    else:
        messages.error(request, "Apenas administradores ou o proprietário da companhia podem remover avaliações.")
        return redirect('company_product_detail', company_id=company.id, product_id=product.id)

def admin_company_delete(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    company.delete()
    return redirect('admin_home')


def add_company(request):
    if request.method == 'POST':
        company_form = CompanyForm(request.POST, request.FILES)
        user_form = UserForm(request.POST)

        if company_form.is_valid() and user_form.is_valid():
            with transaction.atomic():
                # Save the company instance first
                company = company_form.save()

                # Prepare the user data with company info
                user = user_form.save(commit=False)
                user.user_type = 'company'
                user.firstname = 'Company'
                user.lastname = company.name
                user.email = company.email
                user.phone = company.phone
                user.address = company.address
                user.company = company
                user.set_password(user_form.cleaned_data['password'])
                user.save()

                messages.success(request, 'Company and associated user have been created successfully.')
                return redirect('admin_home')
        else:
            messages.error(request, 'Please correct the errors below.')

    else:
        company_form = CompanyForm()
        user_form = UserForm()

    return render(request, 'add_company.html', {
        'company_form': company_form,
        'user_form': user_form,
    })

@login_required
def order_details(request, order_id):
    purchase = get_object_or_404(Purchase, id=order_id, user=request.user)
    products = [
        {
            "name": item.product.name,
            "quantity": item.quantity,
            "unit_price": item.product.price, 
            "total_price": item.quantity * item.product.price, 
            "image_url": item.product.image.url  
        }
        for item in purchase.purchase_products.all()
    ]
    data = {
        "date": purchase.date,
        "total": purchase.total,
        "paymentMethod": purchase.paymentMethod,
        "shippingAddress": purchase.shippingAddress,
        "status": purchase.status,
        "products": products,
    }
    return JsonResponse(data)

@login_required
def apply_discount(request):
    if request.method == 'POST':
        user = request.user
        data = json.loads(request.body)
        discount_code = data.get('discount_code')

        if discount_code and discount_code.lower() == 'primeiracompra':
            # Verificar se o usuário já fez uma compra
            if not Purchase.objects.filter(user=user).exists():
                # Retorna sucesso com o sinal de desconto aplicado
                request.session['discount_applied'] = True
                return JsonResponse({"success": True})
            else:
                return JsonResponse({"success": False, "message": "O código de desconto só é válido para a primeira compra."})
        
        return JsonResponse({"success": False, "message": "Código de desconto inválido."})
    
    return JsonResponse({"success": False, "message": "Método não permitido."}, status=405)


def product_list(request):
    products = Product.objects.all()
    artists = Artist.objects.all()

    # Filter by product type
    product_type = request.GET.get('type')
    if product_type:
        if product_type == 'Vinil':
            products = products.filter(vinil__isnull=False)
            # Use getlist to retrieve all 'genre' parameters and filter out empty values
            genre = next((g for g in request.GET.getlist('genreVinyl') if g), None)
            if genre:
                products = products.filter(vinil__genre=genre)
        elif product_type == 'CD':
            products = products.filter(cd__isnull=False)
            genre = next((g for g in request.GET.getlist('genreCD') if g), None)
            if genre:
                products = products.filter(cd__genre=genre)
        elif product_type == 'Clothing':
            products = products.filter(clothing__isnull=False)
            color = next((c for c in request.GET.getlist('colorClothing') if c), None)
            if color:
                products = products.filter(clothing__color=color)
        elif product_type == 'Accessory':
            products = products.filter(accessory__isnull=False)
            color = next((c for c in request.GET.getlist('colorAccessory') if c), None)
            if color:
                products = products.filter(accessory__color=color)
            size = next((s for s in request.GET.getlist('size') if s), None)
            if size:
                products = products.filter(accessory__size=size)

    # Filter by price range
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        try:
            products = products.filter(price__gte=float(min_price))
        except ValueError:
            pass
    if max_price:
        try:
            products = products.filter(price__lte=float(max_price))
        except ValueError:
            pass

    # Filter by category if provided
    category = request.GET.get('category')
    if category:
        products = products.filter(category=category)

    # Filter by artist ID if provided
    artist_id = request.GET.get('artist')
    if artist_id:
        try:
            products = products.filter(artist_id=int(artist_id))
        except ValueError:
            pass

    return render(request, 'artists_products.html', {
        'products': products,
        'artists': artists,
    })