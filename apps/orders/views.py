from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from .models import Cart, CartItem, Order, OrderItem, OrderTracking, Invoice, PreOrder, RestockNotification
from .serializers import (
    CartSerializer, CartItemSerializer, OrderSerializer, OrderCreateSerializer,
    OrderTrackingSerializer, InvoiceSerializer, PreOrderSerializer, RestockNotificationSerializer
)
from apps.products.models import Product


class CartView(generics.RetrieveAPIView):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        cart, created = Cart.objects.get_or_create(customer=self.request.user)
        return cart


class CartItemListView(generics.ListCreateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        cart, created = Cart.objects.get_or_create(customer=self.request.user)
        return cart.items.all()

    def perform_create(self, serializer):
        cart, created = Cart.objects.get_or_create(customer=self.request.user)
        product_id = serializer.validated_data['product_id']
        
        # Check if item already exists in cart
        existing_item = cart.items.filter(product_id=product_id).first()
        if existing_item:
            existing_item.quantity += serializer.validated_data['quantity']
            existing_item.save()
            return existing_item
        else:
            serializer.save(cart=cart)


class CartItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        cart, created = Cart.objects.get_or_create(customer=self.request.user)
        return cart.items.all()


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def clear_cart(request):
    cart, created = Cart.objects.get_or_create(customer=request.user)
    cart.items.all().delete()
    return Response({'message': 'Cart cleared successfully'})


class OrderListView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'payment_status']
    ordering = ['-created_at']

    def get_queryset(self):
        if self.request.user.is_admin or self.request.user.is_moderator:
            return Order.objects.all()
        elif self.request.user.is_warehouse_manager:
            return Order.objects.filter(status__in=['confirmed', 'processing'])
        else:
            return Order.objects.filter(customer=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OrderCreateSerializer
        return OrderSerializer


class OrderDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_admin or self.request.user.is_moderator:
            return Order.objects.all()
        elif self.request.user.is_warehouse_manager:
            return Order.objects.filter(status__in=['confirmed', 'processing'])
        else:
            return Order.objects.filter(customer=self.request.user)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def cancel_order(request, pk):
    order = get_object_or_404(Order, pk=pk, customer=request.user)
    
    if order.can_be_cancelled:
        order.status = 'cancelled'
        order.save()
        
        # Create tracking entry
        OrderTracking.objects.create(
            order=order,
            status='cancelled',
            description='Order cancelled by customer',
            updated_by=request.user
        )
        
        return Response({'message': 'Order cancelled successfully'})
    else:
        return Response(
            {'error': 'Order cannot be cancelled at this stage'}, 
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def confirm_order(request, pk):
    if not (request.user.is_admin or request.user.is_moderator):
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    order = get_object_or_404(Order, pk=pk)
    
    if order.status == 'pending':
        order.status = 'confirmed'
        order.processed_by = request.user
        order.save()
        
        # Create tracking entry
        OrderTracking.objects.create(
            order=order,
            status='confirmed',
            description='Order confirmed by admin',
            updated_by=request.user
        )
        
        return Response({'message': 'Order confirmed successfully'})
    else:
        return Response(
            {'error': 'Order cannot be confirmed'}, 
            status=status.HTTP_400_BAD_REQUEST
        )


class OrderTrackingView(generics.ListCreateAPIView):
    serializer_class = OrderTrackingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        order_id = self.kwargs['order_id']
        return OrderTracking.objects.filter(order_id=order_id)

    def perform_create(self, serializer):
        order_id = self.kwargs['order_id']
        serializer.save(order_id=order_id, updated_by=self.request.user)


class InvoiceView(generics.RetrieveAPIView):
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_admin or self.request.user.is_moderator:
            return Invoice.objects.all()
        else:
            return Invoice.objects.filter(order__customer=self.request.user)


class PreOrderListView(generics.ListCreateAPIView):
    serializer_class = PreOrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PreOrder.objects.filter(customer=self.request.user)

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)


class RestockNotificationListView(generics.ListCreateAPIView):
    serializer_class = RestockNotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return RestockNotification.objects.filter(customer=self.request.user)

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def order_dashboard(request):
    """Dashboard view for warehouse managers and admins"""
    if not (request.user.is_admin or request.user.is_warehouse_manager):
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    from django.db.models import Count, Sum
    
    # Order statistics
    order_stats = {
        'pending_orders': Order.objects.filter(status='pending').count(),
        'confirmed_orders': Order.objects.filter(status='confirmed').count(),
        'processing_orders': Order.objects.filter(status='processing').count(),
        'shipped_orders': Order.objects.filter(status='shipped').count(),
        'total_revenue': Order.objects.filter(status='delivered').aggregate(
            total=Sum('total_amount')
        )['total'] or 0,
    }
    
    return Response(order_stats)