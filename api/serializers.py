from rest_framework import serializers
from .models import (
    Product,
    Cart,
    CartItem,
    Order,
    OrderItem,
    Customer,
    Category,
)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug"]


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "id",
            "category",
            "title",
            "description",
            "price",
            "image",
            "stock",
            "is_active",
            "created_at",
        ]


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ["id", "telegram_id", "username", "full_name", "created_at"]
        read_only_fields = ["id", "created_at"]


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source="product",
        write_only=True,
    )

    class Meta:
        model = CartItem
        fields = ["id", "product", "product_id", "quantity", "subtotal"]
        read_only_fields = ["id", "subtotal", "product"]


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
    )

    class Meta:
        model = Cart
        fields = [
            "id",
            "customer",
            "created_at",
            "updated_at",
            "items",
            "total_amount",
        ]
        read_only_fields = [
            "id",
            "customer",
            "created_at",
            "updated_at",
            "items",
            "total_amount",
        ]


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "product", "quantity", "price", "subtotal"]
        read_only_fields = ["id", "product", "price", "subtotal"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "customer",
            "status",
            "total_amount",
            "phone",
            "address",
            "created_at",
            "items",
        ]
        read_only_fields = [
            "id",
            "customer",
            "status",
            "total_amount",
            "created_at",
        ]
