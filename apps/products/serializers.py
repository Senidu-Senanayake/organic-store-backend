from rest_framework import serializers
from .models import (
    Category, Product, ProductImage, Stock, ProductReview, 
    Wishlist, Coupon, PromotionalOffer
)


class CategorySerializer(serializers.ModelSerializer):
    subcategories = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = '__all__'

    def get_subcategories(self, obj):
        if obj.subcategories.exists():
            return CategorySerializer(obj.subcategories.all(), many=True).data
        return []


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = '__all__'


class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = '__all__'


class ProductReviewSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.username', read_only=True)

    class Meta:
        model = ProductReview
        fields = '__all__'
        read_only_fields = ('customer', 'is_verified_purchase')


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    stock = StockSerializer(read_only=True)
    reviews = ProductReviewSerializer(many=True, read_only=True)
    average_rating = serializers.ReadOnlyField()
    review_count = serializers.ReadOnlyField()
    is_in_stock = serializers.ReadOnlyField()
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at', 'updated_at')


class ProductListSerializer(serializers.ModelSerializer):
    """Simplified serializer for product lists"""
    primary_image = serializers.SerializerMethodField()
    category_name = serializers.CharField(source='category.name', read_only=True)
    average_rating = serializers.ReadOnlyField()
    is_in_stock = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = ('id', 'name', 'short_description', 'price', 'primary_image', 
                 'category_name', 'average_rating', 'is_in_stock', 'is_featured')

    def get_primary_image(self, obj):
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            return ProductImageSerializer(primary_image).data
        return None


class WishlistSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Wishlist
        fields = '__all__'
        read_only_fields = ('customer',)


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = '__all__'
        read_only_fields = ('created_by', 'used_count')


class PromotionalOfferSerializer(serializers.ModelSerializer):
    applicable_products = ProductListSerializer(many=True, read_only=True)

    class Meta:
        model = PromotionalOffer
        fields = '__all__'
        read_only_fields = ('created_by',)