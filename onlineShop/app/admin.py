from django.contrib import admin

from app.models import Category, Brand, Product, Review, Order, OrderItem

# Register your models here.


admin.site.register([Category, Brand, Product, Review, Order, OrderItem])