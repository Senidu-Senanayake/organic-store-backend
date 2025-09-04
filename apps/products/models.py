from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

User = get_user_model()


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', null=True, blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Product(models.Model):
    AVAILABILITY_CHOICES = (
        ('in_stock', 'In Stock'),
        ('out_of_stock', 'Out of Stock'),
        ('pre_order', 'Pre-Order'),
        ('discontinued', 'Discontinued'),
    )

    name = models.CharField(max_length=200)
    description = models.TextField()
    short_description = models.CharField(max_length=500, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    sku = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    weight = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    dimensions = models.CharField(max_length=100, blank=True)  # Format: "L x W x H"
    availability = models.CharField(max_length=20, choices=AVAILABILITY_CHOICES, default='in_stock')
    is_organic = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.CharField(max_length=500, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_products')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if reviews:
            return sum([review.rating for review in reviews]) / len(reviews)
        return 0

    @property
    def review_count(self):
        return self.reviews.count()

    @property
    def is_in_stock(self):
        return self.stock.quantity > 0 if hasattr(self, 'stock') else False


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Image for {self.product.name}"


class Stock(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='stock')
    quantity = models.PositiveIntegerField(default=0)
    reserved_quantity = models.PositiveIntegerField(default=0)
    reorder_level = models.PositiveIntegerField(default=10)
    max_stock_level = models.PositiveIntegerField(default=1000)
    last_updated = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Stock for {self.product.name}: {self.quantity}"

    @property
    def available_quantity(self):
        return self.quantity - self.reserved_quantity

    @property
    def is_low_stock(self):
        return self.available_quantity <= self.reorder_level


class ProductReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(max_length=200, blank=True)
    comment = models.TextField(blank=True)
    is_verified_purchase = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('product', 'customer')

    def __str__(self):
        return f"Review by {self.customer.username} for {self.product.name}"


class Wishlist(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlisted_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('customer', 'product')

    def __str__(self):
        return f"{self.customer.username}'s wishlist - {self.product.name}"


class ProductComparison(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comparisons')
    products = models.ManyToManyField(Product, related_name='compared_by')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comparison by {self.customer.username}"


class Coupon(models.Model):
    DISCOUNT_TYPES = (
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    )

    code = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=200, blank=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    minimum_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    maximum_uses = models.PositiveIntegerField(null=True, blank=True)
    used_count = models.PositiveIntegerField(default=0)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    applicable_products = models.ManyToManyField(Product, blank=True, related_name='applicable_coupons')
    applicable_categories = models.ManyToManyField(Category, blank=True, related_name='applicable_coupons')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code

    @property
    def is_valid(self):
        from django.utils import timezone
        now = timezone.now()
        return (self.is_active and 
                self.valid_from <= now <= self.valid_to and
                (self.maximum_uses is None or self.used_count < self.maximum_uses))


class PromotionalOffer(models.Model):
    OFFER_TYPES = (
        ('buy_x_get_y', 'Buy X Get Y'),
        ('bulk_discount', 'Bulk Discount'),
        ('seasonal', 'Seasonal Offer'),
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    offer_type = models.CharField(max_length=20, choices=OFFER_TYPES)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    buy_quantity = models.PositiveIntegerField(null=True, blank=True)
    get_quantity = models.PositiveIntegerField(null=True, blank=True)
    applicable_products = models.ManyToManyField(Product, related_name='promotional_offers')
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title