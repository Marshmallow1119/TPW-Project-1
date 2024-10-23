from django.db import models

# Create your models here.
class User(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    email = models.EmailField(max_length=50)
    profile_picture = models.ImageField(upload_to='profile_pictures')
    numberOfPurchases = models.IntegerField(default=0)

class Company(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=50)

class Product(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    description = models.TextField()
    price = models.FloatField()
    image = models.ImageField(upload_to='products/')
    artist = models.CharField(max_length=50)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='products')

