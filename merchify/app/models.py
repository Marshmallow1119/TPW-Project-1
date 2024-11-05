from django.contrib.auth.models import AbstractUser
from django.db import models
from django.template.defaultfilters import default
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    number_of_purchases = models.IntegerField(default=0)
    address = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(max_length=50, unique=True)
    phone = models.CharField(max_length=50, unique=True)
    country=models.CharField(max_length=50, blank=True, null=True)
    image = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return self.username

class Company(models.Model):
    id = models.AutoField(primary_key=True,)
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(max_length=50, unique=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    logo = models.ImageField(upload_to='company_logos', blank=True, null=True)

    def __str__(self):
        return self.name

class Artist(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField();
    image = models.ImageField()

    def __str__(self):
        return self.name

class Product(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    description = models.TextField()
    price = models.FloatField()
    image = models.ImageField(upload_to='products/')
    artist = models.ForeignKey('Artist', on_delete=models.CASCADE)
    company = models.ForeignKey('Company', on_delete=models.CASCADE, related_name='products')
    category = models.CharField(max_length=50)
    addedProduct = models.DateField(auto_now_add=True)

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
    products = models.ManyToManyField(Product, related_name='carts')
    date = models.DateField()
    total = models.FloatField()

    def __str__(self):
        return self.user.username + ' - ' + str(self.date)

class CartItem(models.Model):
    id = models.AutoField(primary_key=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='items')
    quantity = models.IntegerField()
    total = models.FloatField()

    def __str__(self):
        return self.product.name + ' - ' + str(self.quantity)

class Favorite(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='favorites')

    def __str__(self):
        return self.user.username + ' - ' + self.product.name
    
class Purchase(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchases')
    products = models.ManyToManyField(Product, related_name='purchases')
    date = models.DateField()
    total = models.FloatField()
    paymentMethod = models.CharField(max_length=50)
    shippingAddress = models.CharField(max_length=50)
    status = models.CharField(max_length=50)

    def __str__(self):
        return self.user.username + ' - ' + str(self.date)

class Review(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    text = models.TextField()
    rating = models.IntegerField()
    date = models.DateField()

    def __str__(self):
        return self.user.username + ' - ' + self.product.name




