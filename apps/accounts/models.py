from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


class User(AbstractUser):
    USER_ROLES = (
        ('customer', 'Customer'),
        ('admin', 'Admin'),
        ('moderator', 'Moderator'),
        ('warehouse_manager', 'Warehouse Manager'),
    )
    
    role = models.CharField(max_length=20, choices=USER_ROLES, default='customer')
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_customer(self):
        return self.role == 'customer'

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_moderator(self):
        return self.role == 'moderator'

    @property
    def is_warehouse_manager(self):
        return self.role == 'warehouse_manager'


class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    preferred_categories = models.ManyToManyField('products.Category', blank=True)
    newsletter_subscription = models.BooleanField(default=True)
    loyalty_points = models.IntegerField(default=0)
    total_orders = models.IntegerField(default=0)
    total_spent = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Customer Profile: {self.user.username}"


class ModeratorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='moderator_profile')
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assigned_moderators')
    permissions = models.JSONField(default=dict)
    department = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Moderator Profile: {self.user.username}"


class WarehouseManagerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='warehouse_manager_profile')
    warehouse_location = models.CharField(max_length=200, blank=True)
    shift_start = models.TimeField(null=True, blank=True)
    shift_end = models.TimeField(null=True, blank=True)

    def __str__(self):
        return f"Warehouse Manager Profile: {self.user.username}"


class SocialMediaAccount(models.Model):
    PLATFORM_CHOICES = (
        ('facebook', 'Facebook'),
        ('google', 'Google'),
        ('twitter', 'Twitter'),
        ('instagram', 'Instagram'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='social_accounts')
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    social_id = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'platform')

    def __str__(self):
        return f"{self.user.username} - {self.get_platform_display()}"