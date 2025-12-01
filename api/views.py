from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Product, Order, Cart, CartItem, OrderItem, Customer
from .serializers import ProductSerializer, CartSerializer, OrderSerializer


def get_or_create_customer_from_request(request):
    """
    Helper to get or create a Customer based on telegram_id
    coming from query params or request data.
    """
    telegram_id = request.data.get("telegram_id") or request.query_params.get("telegram_id")
    if not telegram_id:
        return None, Response(
            {"detail": "telegram_id is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        telegram_id_int = int(telegram_id)
    except (TypeError, ValueError):
        return None, Response(
            {"detail": "telegram_id must be an integer."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    username = request.data.get("username") or request.query_params.get("username")
    full_name = request.data.get("full_name") or request.query_params.get("full_name")

    customer, _ = Customer.objects.get_or_create(
        telegram_id=telegram_id_int,
        defaults={"username": username, "full_name": full_name},
    )
    return customer, None


class ProductListCreateView(generics.ListCreateAPIView):
    """
    GET /products/  -> list products
    POST /products/ -> create product (optional, for admin/testing)
    """
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /products/<id>/
    PUT/PATCH /products/<id>/
    DELETE /products/<id>/
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = "pk"


class CartView(APIView):
    """
    GET /cart/?telegram_id=123  -> return current cart for user
    """

    def get(self, request):
        customer, error_response = get_or_create_customer_from_request(request)
        if error_response:
            return error_response

        cart, _ = Cart.objects.get_or_create(customer=customer)
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CartAddItemView(APIView):
    """
    POST /cart/add/
    {
        "telegram_id": 123,
        "product_id": 1,
        "quantity": 2
    }
    """

    def post(self, request):
        customer, error_response = get_or_create_customer_from_request(request)
        if error_response:
            return error_response

        product_id = request.data.get("product_id")
        quantity = request.data.get("quantity", 1)

        if not product_id:
            return Response(
                {"detail": "product_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            quantity = int(quantity)
            if quantity <= 0:
                raise ValueError
        except (TypeError, ValueError):
            return Response(
                {"detail": "quantity must be a positive integer."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            product = Product.objects.get(pk=product_id, is_active=True)
        except Product.DoesNotExist:
            return Response(
                {"detail": "Product not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        cart, _ = Cart.objects.get_or_create(customer=customer)

        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={"quantity": quantity},
        )
        if not created:
            item.quantity += quantity
            item.save()

        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CartClearView(APIView):
    """
    POST /cart/clear/
    { "telegram_id": 123 }
    """

    def post(self, request):
        customer, error_response = get_or_create_customer_from_request(request)
        if error_response:
            return error_response

        try:
            cart = Cart.objects.get(customer=customer)
        except Cart.DoesNotExist:
            return Response(
                {"detail": "Cart is already empty."},
                status=status.HTTP_200_OK,
            )

        cart.items.all().delete()
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)


class OrderListCreateView(APIView):
    """
    GET /orders/?telegram_id=123 -> list user's orders
    POST /orders/
    {
        "telegram_id": 123,
        "phone": "...",
        "address": "..."
    }
    Creates order from current cart.
    """

    def get(self, request):
        customer, error_response = get_or_create_customer_from_request(request)
        if error_response:
            return error_response

        orders = Order.objects.filter(customer=customer).order_by("-created_at")
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        customer, error_response = get_or_create_customer_from_request(request)
        if error_response:
            return error_response

        phone = request.data.get("phone", "")
        address = request.data.get("address", "")

        cart, _ = Cart.objects.get_or_create(customer=customer)
        items = cart.items.select_related("product").all()

        if not items:
            return Response(
                {"detail": "Cart is empty."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        total = sum(item.product.price * item.quantity for item in items)

        order = Order.objects.create(
            customer=customer,
            phone=phone,
            address=address,
            total_amount=total,
        )

        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price,
            )
            # optional stock handling
            if item.product.stock is not None:
                item.product.stock = max(0, item.product.stock - item.quantity)
                item.product.save()

        cart.items.all().delete()

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class OrderDetailView(generics.RetrieveAPIView):
    """
    GET /orders/<id>/
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    lookup_field = "pk"