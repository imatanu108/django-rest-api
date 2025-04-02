from django.contrib import admin
from .models import Order, OrderItem, Product

class OrderItemInline(admin.TabularInline):
    model = OrderItem

class OrderAdmin(admin.ModelAdmin):
    inlines = [
        OrderItemInline
    ]

class ProductsAdmin(admin.ModelAdmin):
    model = Product

admin.site.register(Order, OrderAdmin)
admin.site.register(Product, ProductsAdmin)