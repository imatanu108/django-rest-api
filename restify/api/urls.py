from django.urls import path
from . import views


urlpatterns = [
    path('products/', views.product_list),
    path('products/list-create/', views.ProductListCreateAPIView.as_view()),
    path('products/create/', views.ProductCreateAPIView.as_view()),
    path('products/all/', views.ProductListAPIView.as_view()), # Using Generic View
    path('products/mixins/', views.ProductListMixinAPIView.as_view()), # Using Generic View with Mixins
    path('products/info/', views.product_info),
    path('products/all/info/', views.ProductInfoAPIView.as_view()), # using class base APIView
    path('products/<int:pk>/', views.product_detail),
    path('products/all/<int:product_id>/', views.ProductDetailAPIView.as_view()), # Using Generic View
    path('orders/', views.order_list),
    path('orders/all/', views.OrderListAPIView.as_view()), # Using Generic View
    path('user-orders/', views.UserOrderListAPIView.as_view(), name='user-orders'), # Using Generic View
]

