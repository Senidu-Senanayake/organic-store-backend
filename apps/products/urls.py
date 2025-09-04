from django.urls import path
from . import views

urlpatterns = [
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('categories/<int:pk>/', views.CategoryDetailView.as_view(), name='category-detail'),
    path('', views.ProductListView.as_view(), name='product-list'),
    path('<int:pk>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('search/', views.product_search, name='product-search'),
    path('<int:product_id>/reviews/', views.ProductReviewListView.as_view(), name='product-reviews'),
    path('wishlist/', views.WishlistView.as_view(), name='wishlist'),
    path('wishlist/<int:pk>/', views.WishlistItemView.as_view(), name='wishlist-item'),
    path('stock/', views.StockListView.as_view(), name='stock-list'),
    path('stock/<int:pk>/', views.StockDetailView.as_view(), name='stock-detail'),
    path('coupons/', views.CouponListView.as_view(), name='coupon-list'),
    path('coupons/validate/', views.validate_coupon, name='validate-coupon'),
    path('offers/', views.PromotionalOfferListView.as_view(), name='promotional-offers'),
]