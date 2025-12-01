from django.urls import path
from .views import (
    ProductListCreateView,
    ProductDetailView,
    CartView,
    CartAddItemView,
    CartClearView,
    OrderListCreateView,
    OrderDetailView,
)


# api/urls.py
urlpatterns = [
    path("products/", ProductListCreateView.as_view(), name="product-list"),
    path("products/<int:pk>/", ProductDetailView.as_view(), name="product-detail"),

    path("cart/", CartView.as_view(), name="cart-detail"),
    path("cart/add/", CartAddItemView.as_view(), name="cart-add-item"),
    path("cart/clear/", CartClearView.as_view(), name="cart-clear"),

    path("orders/", OrderListCreateView.as_view(), name="order-list-create"),
    path("orders/<int:pk>/", OrderDetailView.as_view(), name="order-detail"),
]