from rest_framework import generics, permissions, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import (
    Category, Product, ProductImage, Stock, ProductReview, 
    Wishlist, Coupon, PromotionalOffer
)
from .serializers import (
    CategorySerializer, ProductSerializer, ProductListSerializer,
    ProductImageSerializer, StockSerializer, ProductReviewSerializer,
    WishlistSerializer, CouponSerializer, PromotionalOfferSerializer
)


class CategoryListView(generics.ListCreateAPIView):
    queryset = Category.objects.filter(is_active=True, parent=None)
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class ProductListView(generics.ListCreateAPIView):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'availability', 'is_featured', 'is_organic']
    search_fields = ['name', 'description', 'short_description']
    ordering_fields = ['price', 'created_at', 'name']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ProductSerializer
        return ProductListSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def product_search(request):
    query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    
    products = Product.objects.filter(is_active=True)
    
    if query:
        products = products.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) |
            Q(short_description__icontains=query)
        )
    
    if category_id:
        products = products.filter(category_id=category_id)
    
    if min_price:
        products = products.filter(price__gte=min_price)
    
    if max_price:
        products = products.filter(price__lte=max_price)
    
    serializer = ProductListSerializer(products, many=True)
    return Response(serializer.data)


class ProductReviewListView(generics.ListCreateAPIView):
    serializer_class = ProductReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        product_id = self.kwargs['product_id']
        return ProductReview.objects.filter(product_id=product_id, is_approved=True)

    def perform_create(self, serializer):
        product_id = self.kwargs['product_id']
        serializer.save(customer=self.request.user, product_id=product_id)


class WishlistView(generics.ListCreateAPIView):
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Wishlist.objects.filter(customer=self.request.user)

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)


class WishlistItemView(generics.DestroyAPIView):
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Wishlist.objects.filter(customer=self.request.user)


class StockListView(generics.ListAPIView):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['product__category']

    def get_queryset(self):
        if self.request.user.is_warehouse_manager or self.request.user.is_admin:
            return Stock.objects.all()
        return Stock.objects.none()


class StockDetailView(generics.RetrieveUpdateAPIView):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_warehouse_manager or self.request.user.is_admin:
            return Stock.objects.all()
        return Stock.objects.none()

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


class CouponListView(generics.ListCreateAPIView):
    queryset = Coupon.objects.filter(is_active=True)
    serializer_class = CouponSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_admin:
            return Coupon.objects.all()
        return Coupon.objects.filter(is_active=True)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def validate_coupon(request):
    code = request.data.get('code', '')
    order_amount = request.data.get('order_amount', 0)
    
    try:
        coupon = Coupon.objects.get(code=code, is_active=True)
        if coupon.is_valid and order_amount >= coupon.minimum_amount:
            return Response({
                'valid': True,
                'coupon': CouponSerializer(coupon).data,
                'message': 'Coupon is valid'
            })
        else:
            return Response({
                'valid': False,
                'message': 'Coupon is not valid or minimum amount not met'
            }, status=status.HTTP_400_BAD_REQUEST)
    except Coupon.DoesNotExist:
        return Response({
            'valid': False,
            'message': 'Coupon not found'
        }, status=status.HTTP_404_NOT_FOUND)


class PromotionalOfferListView(generics.ListCreateAPIView):
    queryset = PromotionalOffer.objects.filter(is_active=True)
    serializer_class = PromotionalOfferSerializer
    permission_classes = [permissions.AllowAny]

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)