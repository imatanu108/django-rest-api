from django.urls import path
from . import views


urlpatterns = [
    path('products/', views.product_list),
    path('products/all/', views.ProductListAPIView.as_view()), # Using Generic View
    path('products/info/', views.product_info),
    path('products/<int:pk>/', views.product_detail),
    path('products/all/<int:pk>/', views.ProductDetailAPIView.as_view()), # Using Generic View
    path('orders/', views.order_list),
    path('orders/all/', views.OrderListAPIView.as_view()), # Using Generic View
    path('user-orders/', views.UserOrderListAPIView.as_view(), name='user-orders'), # Using Generic View
]

