from django.urls import path
from . import views

urlpatterns = [
    path('', views.NotificationListView.as_view(), name='notification-list'),
    path('<int:pk>/read/', views.mark_notification_read, name='mark-notification-read'),
    path('mark-all-read/', views.mark_all_notifications_read, name='mark-all-notifications-read'),
    path('messages/', views.ChatMessageListView.as_view(), name='chat-messages'),
    path('tickets/', views.CustomerSupportTicketListView.as_view(), name='support-tickets'),
    path('tickets/<int:pk>/', views.CustomerSupportTicketDetailView.as_view(), name='support-ticket-detail'),
    path('tickets/<int:ticket_id>/messages/', views.TicketMessageListView.as_view(), name='ticket-messages'),
    path('email-templates/', views.EmailTemplateListView.as_view(), name='email-templates'),
    path('dashboard/', views.notification_dashboard, name='notification-dashboard'),
]