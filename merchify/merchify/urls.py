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
    path('home/', views.home, name='home'),
    path('admin_home/', views.admin_home, name='admin_home'),
    path('produtos/', views.produtos, name='produtos'),
    path('artists/', views.artistas, name='artistas'),
    path('login/', views.login, name='login'),
    path("logout", views.logout, name="logout"),
    path('products/<str:name>/', views.artistsProducts, name='artistsProducts'),
    path('product/<int:identifier>/',  views.productDetails, name='productDetails'),
    path('search/', views.search_products, name='search_products'),
    path('register/', views.register, name='register'),
    path('cart/', views.viewCart, name='cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name = 'add_to_cart'),
    path('remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path("account/profile", views.profile, name="profile"),
    path("product/<int:product_id>/submit_review/", views.submit_review, name="submit_review"),
    path('company/<int:company_id>/products/', views.company_products, name='company_products'),
    path('company/<int:company_id>/add-product/', views.add_product_to_company, name='add_product_to_company'),
    path('company/<int:company_id>/product/<int:product_id>/detail/', views.company_product_detail, name='company_product_detail'),
    path('review/<int:review_id>/delete/', views.delete_review, name='delete_review'),  
    path('product/<int:product_id>/edit/', views.edit_product, name='edit_product'),
    path('product/<int:product_id>/delete/', views.delete_product, name='delete_product'),
    path("favorites/", views.checkfavorite, name="favorites"),
    path('favorites/add/<int:product_id>/', views.addtofavorite, name='addtofavorite'),
    path('favorites/remove/<int:product_id>/', views.remove_from_favorites, name='remove_from_favorites'),
    path('payment/', views.payment_page, name='payment_page'),
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('process_payment/', views.process_payment, name='process_payment'),
    path('payment-confirmation/', views.payment_confirmation, name='payment_confirmation'),
    path('admin_home/delete/<int:product_id>', views.admin_product_delete, name='admin_product_delete'),
    path('admin_home/delete/company/<int:company_id>', views.admin_company_delete, name='admin_company_delete'),
    path('admin_home/add/company',views.add_company, name='add_company'),
    path('products/', views.product_list, name='product_list'),
    path('account/order_details/<int:order_id>/', views.order_details, name='order_details'),
    path('delete/review/<int:review_id>/', views.delete_review, name='delete_review'),
    path('apply_discount/', views.apply_discount, name='apply_discount'),
    path('companhias/', views.companhias, name='companhias'),
]   


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)