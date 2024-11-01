"""
URL configuration for merchify project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('home/', views.home, name='home_login'),
    path('produtos/', views.produtos, name='produtos'),
    path('artists/', views.artistas, name='artistas'),
    path('login/', views.login, name='login'),
    path("logout", views.logout, name="logout"),
    path('products/<str:name>/', views.artistsProducts, name='artistsProducts'),
    path('product/<int:identifier>/',  views.productDetails, name='productDetails'),
    path('/search', views.search_products, name='search_products'),
    path('register/', views.register, name='register'),
    path('cart/', views.viewCart, name='cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name = 'add_to_cart'),
    path('remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),

]   


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)