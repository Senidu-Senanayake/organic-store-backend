# Organic Store E-Commerce Backend

A comprehensive Django REST API backend for an organic e-commerce platform based on the Trustcare Holdings system requirements.

## Features

### User Management
- Multi-role authentication (Customer, Admin, Moderator, Warehouse Manager)
- JWT token-based authentication
- User profiles with role-specific data
- Social media account integration

### Product Management
- Product catalog with categories and subcategories
- Stock management and inventory tracking
- Product reviews and ratings
- Wishlist functionality
- Product comparison
- Coupon and promotional offer system

### Order Management
- Shopping cart functionality
- Order processing workflow
- Order tracking and status updates
- Invoice generation
- Pre-order system
- Restock notifications

### Communication & Support
- Real-time notifications
- Customer support ticketing system
- Chat messaging system
- Email templates

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd organic-store-backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Database Setup**
   - Install MySQL and create a database named `organic_store`
   - Copy `.env.example` to `.env` and update database credentials
   ```bash
   cp .env.example .env
   ```

5. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

## API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `POST /api/auth/token/refresh/` - Refresh JWT token
- `GET /api/auth/profile/` - Get user profile
- `PUT /api/auth/profile/` - Update user profile

### Products
- `GET /api/products/` - List products
- `POST /api/products/` - Create product (Admin only)
- `GET /api/products/{id}/` - Get product details
- `PUT /api/products/{id}/` - Update product (Admin only)
- `DELETE /api/products/{id}/` - Delete product (Admin only)
- `GET /api/products/search/` - Search products
- `GET /api/products/categories/` - List categories
- `GET /api/products/wishlist/` - Get user wishlist
- `POST /api/products/wishlist/` - Add to wishlist

### Orders
- `GET /api/orders/` - List orders
- `POST /api/orders/` - Create order
- `GET /api/orders/{id}/` - Get order details
- `POST /api/orders/{id}/cancel/` - Cancel order
- `GET /api/orders/cart/` - Get shopping cart
- `POST /api/orders/cart/items/` - Add item to cart
- `PUT /api/orders/cart/items/{id}/` - Update cart item
- `DELETE /api/orders/cart/items/{id}/` - Remove from cart

### Notifications
- `GET /api/notifications/` - List notifications
- `POST /api/notifications/{id}/read/` - Mark notification as read
- `GET /api/notifications/tickets/` - List support tickets
- `POST /api/notifications/tickets/` - Create support ticket
- `GET /api/notifications/messages/` - List chat messages
- `POST /api/notifications/messages/` - Send chat message

## User Roles & Permissions

### Customer
- Browse and search products
- Manage shopping cart and wishlist
- Place and track orders
- Write product reviews
- Access customer support

### Admin
- Full system access
- Manage users, products, and orders
- Create coupons and promotional offers
- View analytics and reports
- Manage moderators and warehouse managers

### Moderator
- Assist customers with queries
- Monitor customer accounts
- Handle support tickets
- Reply to chat messages

### Warehouse Manager
- View and manage orders
- Update stock levels
- Track deliveries
- Acknowledge confirmed orders

## Database Schema

The system uses MySQL with the following main models:
- **User**: Extended Django user with roles
- **Product**: Product catalog with categories
- **Order**: Order management system
- **Cart**: Shopping cart functionality
- **Notification**: System notifications
- **CustomerSupportTicket**: Support system

## Environment Variables

Create a `.env` file with the following variables:
```
SECRET_KEY=your-secret-key
DEBUG=True
DB_NAME=organic_store
DB_USER=root
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=3306
```

## Development

### Running Tests
```bash
python manage.py test
```

### Creating Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Collecting Static Files
```bash
python manage.py collectstatic
```

## Deployment

For production deployment:
1. Set `DEBUG=False` in environment variables
2. Configure proper database settings
3. Set up email backend for notifications
4. Configure static file serving
5. Use a production WSGI server like Gunicorn

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License.