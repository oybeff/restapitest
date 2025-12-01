from django.contrib import admin
from .models import Customer, Category, Product, Cart, CartItem, Order, OrderItem


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("id", "telegram_id", "username", "full_name", "created_at")
    search_fields = ("telegram_id", "username", "full_name")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "category", "price", "stock", "is_active", "created_at")
    list_filter = ("category", "is_active")
    search_fields = ("title",)
    list_editable = ("price", "stock", "is_active")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "status", "total_amount", "phone", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("customer__telegram_id", "customer__username", "phone")


# Simpler registration for these; you can customize later if needed.
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(OrderItem)