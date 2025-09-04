#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'organic_store.settings')
django.setup()

from apps.products.models import Category, Product, Stock
from apps.accounts.models import User
from decimal import Decimal

def create_sample_data():
    # Create categories
    categories = [
        {'name': 'Fruits & Vegetables', 'description': 'Fresh organic fruits and vegetables'},
        {'name': 'Dairy & Eggs', 'description': 'Organic dairy products and farm fresh eggs'},
        {'name': 'Grains & Cereals', 'description': 'Organic grains, cereals, and pulses'},
        {'name': 'Beverages', 'description': 'Organic juices, teas, and healthy drinks'},
        {'name': 'Snacks', 'description': 'Healthy organic snacks and treats'},
    ]
    
    created_categories = []
    for cat_data in categories:
        category, created = Category.objects.get_or_create(
            name=cat_data['name'],
            defaults={'description': cat_data['description']}
        )
        created_categories.append(category)
        if created:
            print(f"Created category: {category.name}")
    
    # Create sample products
    admin_user = User.objects.filter(role='admin').first()
    
    products = [
        {
            'name': 'Organic Apples',
            'description': 'Fresh organic red apples from local farms',
            'short_description': 'Crisp and sweet organic apples',
            'category': created_categories[0],
            'sku': 'ORG-APPLE-001',
            'price': Decimal('4.99'),
            'cost_price': Decimal('2.50'),
            'weight': Decimal('1.00'),
            'is_featured': True,
            'stock_quantity': 100
        },
        {
            'name': 'Organic Bananas',
            'description': 'Naturally ripened organic bananas',
            'short_description': 'Sweet and nutritious organic bananas',
            'category': created_categories[0],
            'sku': 'ORG-BANANA-001',
            'price': Decimal('3.49'),
            'cost_price': Decimal('1.75'),
            'weight': Decimal('1.00'),
            'stock_quantity': 150
        },
        {
            'name': 'Organic Whole Milk',
            'description': 'Fresh organic whole milk from grass-fed cows',
            'short_description': 'Creamy organic whole milk',
            'category': created_categories[1],
            'sku': 'ORG-MILK-001',
            'price': Decimal('5.99'),
            'cost_price': Decimal('3.00'),
            'weight': Decimal('1.00'),
            'stock_quantity': 50
        },
        {
            'name': 'Organic Brown Rice',
            'description': 'Nutritious organic brown rice',
            'short_description': 'Whole grain organic brown rice',
            'category': created_categories[2],
            'sku': 'ORG-RICE-001',
            'price': Decimal('8.99'),
            'cost_price': Decimal('4.50'),
            'weight': Decimal('2.00'),
            'stock_quantity': 75
        },
        {
            'name': 'Organic Green Tea',
            'description': 'Premium organic green tea leaves',
            'short_description': 'Antioxidant-rich organic green tea',
            'category': created_categories[3],
            'sku': 'ORG-TEA-001',
            'price': Decimal('12.99'),
            'cost_price': Decimal('6.50'),
            'weight': Decimal('0.25'),
            'is_featured': True,
            'stock_quantity': 200
        }
    ]
    
    for prod_data in products:
        stock_qty = prod_data.pop('stock_quantity')
        product, created = Product.objects.get_or_create(
            sku=prod_data['sku'],
            defaults={**prod_data, 'created_by': admin_user}
        )
        
        if created:
            print(f"Created product: {product.name}")
            
            # Create stock for the product
            Stock.objects.create(
                product=product,
                quantity=stock_qty,
                reorder_level=10,
                max_stock_level=500,
                updated_by=admin_user
            )
            print(f"Created stock for {product.name}: {stock_qty} units")

if __name__ == '__main__':
    create_sample_data()
    print("\nSample data created successfully!")
    print("You can now access the admin panel at: http://localhost:8000/admin/")
    print("Username: admin")
    print("Password: admin123")