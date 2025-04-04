from django.http import JsonResponse
from django.db.models import Max
from .serializers import (
    ProductInfoSerializer,
    ProductSerializer,
    ProductCreateSerializer,
    OrderSerializer,
    OrderItemSerializer,
    OrderCreateSerializer
)
from .models import Product, Order, OrderItem
from rest_framework.response import Response
from rest_framework.decorators import api_view, action
from django.shortcuts import get_object_or_404
from rest_framework import generics, mixins
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.views import APIView
from .filters import ProductFilter, InStockFilterBackend, OrderFilter
from rest_framework import filters, viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination

@api_view(["GET"])
def product_list(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

# Generic view for the same task
class ProductListAPIView(generics.ListAPIView):
    queryset = Product.objects.filter(stock__gt=0)
    serializer_class = ProductSerializer


# Using Mixins with Generic Views to do the same task
class ProductListMixinAPIView(mixins.ListModelMixin, generics.GenericAPIView):
    queryset = Product.objects.filter(stock__gt=0)
    serializer_class = ProductSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


# adding a new product
class ProductCreateAPIView(generics.CreateAPIView):
    model = Product
    serializer_class = ProductCreateSerializer

    # docs: https://www.cdrf.co/
    def create(self, request, *args, **kwargs):
        print(request.data)
        return super().create(request,  *args, **kwargs)
    

# Generic view for the Listing and creating products (with custom permission)
class ProductListCreateAPIView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    # filterset_fields = ('name', 'price')
    filterset_class = ProductFilter
    filter_backends = [
        DjangoFilterBackend, 
        filters.SearchFilter,
        filters.OrderingFilter,
        InStockFilterBackend
    ]
    search_fields = ['=name', 'description'],
    # =name, here name must be exact to get matched but not for the description, to do the same with name we must use only 'name' instead of =name
    ordering_fields = ['name', 'price', 'stock']
    # pagination_class = LimitOffsetPagination
    pagination_class = PageNumberPagination
    pagination_class.page_size = 4 #setting page size for a particular view
    pagination_class.page_size_query_param = 'size'
    pagination_class.max_page_size = 10 # limiting max page size


    def get_permissions(self):
        self.permission_classes = [AllowAny]
        if self.request.method == 'POST':
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()

@api_view(["GET"])
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    serializer = ProductSerializer(product)
    return Response(serializer.data)


# Generic view for the same task
# class ProductDetailAPIView(generics.RetrieveAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer
#     lookup_url_kwarg = 'product_id'


# Single Generic view for the retriving, updating and deleting
class ProductDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_url_kwarg = 'product_id'

    def get_permissions(self):
        self.permission_classes = [AllowAny]
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()


@api_view(["GET"])
def order_list(request):
    orders = Order.objects.prefetch_related("items__product")
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


# generic view
class OrderListAPIView(generics.ListAPIView):
    queryset = Order.objects.prefetch_related("items__product")
    serializer_class = OrderSerializer


# getting orders of the current user
class UserOrderListAPIView(generics.ListAPIView):
    queryset = Order.objects.prefetch_related("items__product")
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        return qs.filter(user=user)


@api_view(["GET"])
def product_info(request):
    products = Product.objects.all()
    serializer = ProductInfoSerializer({
            "products": products,
            "count": len(products),
            "max_price": products.aggregate(max_price=Max("price"))["max_price"],
    })

    return Response(serializer.data)


# Class base API views
class ProductInfoAPIView(APIView):
    def get(self, request):
        products = Product.objects.all()
        serializer = ProductInfoSerializer(
            {
                "products": products,
                "count": len(products),
                "max_price": products.aggregate(max_price=Max("price"))["max_price"],
            }
        )
        return Response(serializer.data)


# Viewsets
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.prefetch_related("items__product")
    serializer_class = OrderSerializer
    permission_classes = [AllowAny]
    pagination_class = None
    filterset_class = OrderFilter
    filter_backends = [DjangoFilterBackend]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        # we can also check with request.method == 'POST'
        if self.action == 'create':
            return OrderCreateSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(user = self.request.user)
        return qs

    @action(
        detail=False, 
        methods=['get'], 
        url_path='user-orders',
        permission_classes=[IsAuthenticated]
    )
    def user_orders(self, request):
        orders = self.get_queryset().filter(user=request.user)
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)