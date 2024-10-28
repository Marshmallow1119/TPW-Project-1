from django.contrib import admin
from .models import Artist
from .models import Product
# Register your models here.
admin.site.register(Artist)
admin.site.register(Product)