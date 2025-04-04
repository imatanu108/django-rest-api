from django.contrib import admin
from .models import Order, OrderItem, Product, User

class OrderItemInline(admin.TabularInline):
    model = OrderItem

class OrderAdmin(admin.ModelAdmin):
    inlines = [
        OrderItemInline
    ]

class ProductsAdmin(admin.ModelAdmin):
    model = Product

class UserAdmin(admin.ModelAdmin):
    model = User

admin.site.register(Order, OrderAdmin)
admin.site.register(Product, ProductsAdmin)
admin.site.register(User, UserAdmin)