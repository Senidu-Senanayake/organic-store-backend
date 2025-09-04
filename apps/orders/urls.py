from django.urls import path
from . import views

urlpatterns = [
    path('cart/', views.CartView.as_view(), name='cart'),
    path('cart/items/', views.CartItemListView.as_view(), name='cart-items'),
    path('cart/items/<int:pk>/', views.CartItemDetailView.as_view(), name='cart-item-detail'),
    path('cart/clear/', views.clear_cart, name='clear-cart'),
    path('', views.OrderListView.as_view(), name='order-list'),
    path('<int:pk>/', views.OrderDetailView.as_view(), name='order-detail'),
    path('<int:pk>/cancel/', views.cancel_order, name='cancel-order'),
    path('<int:pk>/confirm/', views.confirm_order, name='confirm-order'),
    path('<int:order_id>/tracking/', views.OrderTrackingView.as_view(), name='order-tracking'),
    path('invoices/<int:pk>/', views.InvoiceView.as_view(), name='invoice-detail'),
    path('pre-orders/', views.PreOrderListView.as_view(), name='pre-order-list'),
    path('restock-notifications/', views.RestockNotificationListView.as_view(), name='restock-notifications'),
    path('dashboard/', views.order_dashboard, name='order-dashboard'),
]