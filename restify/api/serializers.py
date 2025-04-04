from rest_framework import serializers
from .models import Product, Order, OrderItem
from django.db import transaction

# serializer to get product details
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            'id',
            'name',
            'price',
            'stock',
            'description'
        )

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Price must be greater than 0."
            )
        return value
    

# serializer to create add a product
class ProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            'description',
            'name',
            'price',
            'stock'
        )

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Price must be greater than 0."
            )
        return value


class OrderItemSerializer(serializers.ModelSerializer):
    # Nested serializer to include full product details (use only when needed)
    product = ProductSerializer()

    # Instead of returning the whole product object, we can extract only necessary fields
    product_name = serializers.CharField(source='product.name')
    product_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        source='product.price'
    )

    class Meta:
        model = OrderItem
        fields = (
            'product',        # Returns full product details (nested)
            'quantity',
            'product_name',   # Sends only product name in response
            'product_price',  # Sends only product price in response
            'item_subtotal'   # Uses model's property to calculate subtotal
        )


class OrderCreateSerializer(serializers.ModelSerializer):
    class OrderItemCreateSerializer(serializers.ModelSerializer):
        class Meta:
            model = OrderItem
            fields = ('product', 'quantity')

    order_id = serializers.UUIDField(read_only = True)
    items = OrderItemCreateSerializer(many=True, required=False)

    def update(self, instance, validated_data):
        orderitem_data = validated_data.pop('items', None)
        instance = super().update(instance, validated_data)

        with transaction.atomic():
            if orderitem_data is not None:
                # clearing existing data(optional)
                instance.items.all().delete()

                # recreating items with updated data
                for item in orderitem_data:
                    OrderItem.objects.create(order=instance, **item)

        return instance

    def create(self, validated_data):
        orderitem_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)

        with transaction.atomic():
            for item in orderitem_data:
                OrderItem.objects.create(order=order, **item)

        return order

    class Meta:
        model = Order
        fields = (
            'order_id',
            'user',
            'status',
            'items'
        )
        extra_kwargs = {
            'user': {'read_only': True}
        }


class OrderSerializer(serializers.ModelSerializer):
    order_id = serializers.UUIDField(read_only = True)
    items = OrderItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, obj):
        order_items = obj.items.all()
        return sum(order_item.item_subtotal for order_item in order_items)

    class Meta:
        model = Order
        fields = (
            'order_id',
            'created_at',
            'user',
            'status',
            'items',
            'total_price'
        )


# using generic serializer
class ProductInfoSerializer(serializers.Serializer):
    # get all products, count of products, max price
    products = ProductSerializer(many=True)
    count = serializers.IntegerField()
    max_price = serializers.FloatField()
