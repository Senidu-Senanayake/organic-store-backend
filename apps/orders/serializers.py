from rest_framework import serializers
from .models import Cart, CartItem, Order, OrderItem, OrderTracking, Invoice, PreOrder, RestockNotification
from apps.products.serializers import ProductListSerializer


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    subtotal = serializers.ReadOnlyField()

    class Meta:
        model = CartItem
        fields = '__all__'
        read_only_fields = ('cart',)


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.ReadOnlyField()
    total_amount = serializers.ReadOnlyField()

    class Meta:
        model = Cart
        fields = '__all__'
        read_only_fields = ('customer',)


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'


class OrderTrackingSerializer(serializers.ModelSerializer):
    updated_by_name = serializers.CharField(source='updated_by.username', read_only=True)

    class Meta:
        model = OrderTracking
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    tracking = OrderTrackingSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source='customer.username', read_only=True)

    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ('customer', 'order_number', 'created_at', 'updated_at')


class OrderCreateSerializer(serializers.ModelSerializer):
    items = serializers.ListField(write_only=True)

    class Meta:
        model = Order
        fields = ('shipping_name', 'shipping_address', 'shipping_city', 'shipping_state',
                 'shipping_postal_code', 'shipping_country', 'shipping_phone',
                 'billing_name', 'billing_address', 'billing_city', 'billing_state',
                 'billing_postal_code', 'billing_country', 'customer_notes',
                 'coupon_code', 'items')

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(customer=self.context['request'].user, **validated_data)
        
        # Create order items and calculate totals
        subtotal = 0
        for item_data in items_data:
            product_id = item_data['product_id']
            quantity = item_data['quantity']
            
            from apps.products.models import Product
            product = Product.objects.get(id=product_id)
            
            order_item = OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                unit_price=product.price
            )
            subtotal += order_item.total_price
        
        # Calculate totals (simplified)
        order.subtotal = subtotal
        order.total_amount = subtotal  # Add shipping, tax calculation here
        order.save()
        
        return order


class InvoiceSerializer(serializers.ModelSerializer):
    order = OrderSerializer(read_only=True)

    class Meta:
        model = Invoice
        fields = '__all__'


class PreOrderSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    customer_name = serializers.CharField(source='customer.username', read_only=True)

    class Meta:
        model = PreOrder
        fields = '__all__'
        read_only_fields = ('customer',)


class RestockNotificationSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    customer_name = serializers.CharField(source='customer.username', read_only=True)

    class Meta:
        model = RestockNotification
        fields = '__all__'
        read_only_fields = ('customer',)