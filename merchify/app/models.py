from django.db import models
from django.db.models import Avg
from django.template.defaultfilters import default
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class Company(models.Model):
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(max_length=50, unique=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    logo = models.ImageField(upload_to='company_logos', blank=True, null=True)

    def getNumberOfProducts(self):
        return self.products.count()

    def get_average_rating(self):
        average_rating = self.products.aggregate(avg_rating=Avg('reviews__rating'))['avg_rating']
        return average_rating if average_rating is not None else "Sem Avaliações"

    def __str__(self):
        return self.name

class User(AbstractUser):
    USER_TYPES = (
        ('individual', 'Individual'),
        ('company', 'Company'),
        ('admin', 'Admin')
    )

    firstname = models.CharField(max_length=50, blank=True, null=True)
    lastname = models.CharField(max_length=50, blank=True, null=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='individual')
    number_of_purchases = models.IntegerField(default=0)
    address = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(max_length=50, unique=True, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, unique=True)
    country = models.CharField(max_length=50, blank=True, null=True)
    image = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, blank=True, null=True)


    def __str__(self):
        return self.username



class Artist(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField();
    image = models.ImageField()
    background_image = models.ImageField(upload_to='background_images/', blank=True, null=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    description = models.TextField()
    price = models.FloatField(default=30, null=True)
    image = models.ImageField(upload_to='products/')
    artist = models.ForeignKey('Artist', on_delete=models.CASCADE, null=True)
    company = models.ForeignKey('Company', on_delete=models.CASCADE, related_name='products', null=True)
    category = models.CharField(max_length=50)
    addedProduct = models.DateField(auto_now_add=True, null=True)
    count = models.IntegerField(default=0)

    def get_average_rating(self):
        average_rating = self.reviews.aggregate(avg_rating=Avg('rating'))['avg_rating']
        return average_rating if average_rating is not None else "Sem Avaliações"


    def get_product_type(self):
        if hasattr(self, 'vinil'):
            return 'Vinil'
        elif hasattr(self, 'cd'):
            return 'CD'
        elif hasattr(self, 'clothing'):
            return 'Clothing'
        elif hasattr(self, 'accessory'):
            return 'Accessory'
        return 'Product'
    
    def get_stock(self):
        if hasattr(self, 'vinil'):
            return self.vinil.stock
        elif hasattr(self, 'cd'):
            return self.cd.stock
        elif hasattr(self, 'clothing'):
            return sum(size.stock for size in self.clothing.sizes.all())
        elif hasattr(self, 'accessory'):
            return self.accessory.stock
        return None 

    def __str__(self):
        return self.name

class Size(models.Model):
    clothing = models.ForeignKey('Clothing', on_delete=models.CASCADE, related_name='sizes')
    size = models.CharField(max_length=50)
    stock = models.IntegerField()

    def __str__(self):
        return f"{self.clothing.name} - Size: {self.size}"

class Vinil(Product):
    genre = models.CharField(max_length=50)
    lpSize = models.CharField(max_length=5)
    releaseDate = models.DateField()
    stock = models.IntegerField(default=30)

    def __str__(self):
        return f"{self.name} - {self.artist}"

class CD(Product):
    genre = models.CharField(max_length=50)
    releaseDate = models.DateField()
    stock = models.IntegerField(default=30)

    def __str__(self):
        return f"{self.name} - {self.artist}"

class Clothing(Product):
    color = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name} - {self.artist}"

class Accessory(Product):
    material = models.CharField(max_length=50)
    color = models.CharField(max_length=50)
    size = models.CharField(max_length=50)
    stock = models.IntegerField(default=30)

    def __str__(self):
        return f"{self.name} - {self.artist}"
    
class Cart(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carts')
    date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - {self.date}"

    @property
    def total(self):
        return sum(item.total for item in self.items.all())


class CartItem(models.Model):
    id = models.AutoField(primary_key=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='items')
    quantity = models.IntegerField()
    size = models.ForeignKey(Size, on_delete=models.CASCADE, null=True, blank=True)

    @property
    def total(self):
        return self.quantity * self.product.price

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"

class Favorite(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='favorites')
    def __str__(self):
        return self.user.username + ' - ' + self.product.name

class FavoriteArtist(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favoritesArtist')
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='favoritesArtist',null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.artist.name}"

class FavoriteCompany(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favoriteCompany')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='favoriteCompany', null=True,
                                   blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.company.name}"


class Purchase(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchases')
    date = models.DateField()
    paymentMethod = models.CharField(max_length=50)
    shippingAddress = models.CharField(max_length=50)
    status = models.CharField(max_length=50)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  
    discount_applied = models.BooleanField(default=False)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Adicionado
    
    def __str__(self):
        return self.user.username + ' - ' + str(self.date)
    
    @property
    def total(self):
        return sum(item.total for item in self.purchase_products.all())

class Review(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    text = models.TextField()
    rating = models.IntegerField()
    date = models.DateField()

    def __str__(self):
        return self.user.username + ' - ' + self.product.name



class PurchaseProduct(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name='purchase_products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_purchases')
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.purchase} - {self.product.name} x {self.quantity}"
    
    @property
    def total(self):
        return self.quantity * self.product.price