from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('customer-profile/', views.CustomerProfileView.as_view(), name='customer-profile'),
    path('moderators/', views.ModeratorListView.as_view(), name='moderator-list'),
    path('warehouse-managers/', views.WarehouseManagerListView.as_view(), name='warehouse-manager-list'),
]