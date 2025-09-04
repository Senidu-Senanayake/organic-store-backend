from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Notification, ChatMessage, CustomerSupportTicket, TicketMessage, EmailTemplate
from .serializers import (
    NotificationSerializer, ChatMessageSerializer, CustomerSupportTicketSerializer,
    TicketMessageSerializer, EmailTemplateSerializer
)


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['notification_type', 'is_read']
    ordering = ['-created_at']

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_notification_read(request, pk):
    try:
        notification = Notification.objects.get(pk=pk, recipient=request.user)
        notification.is_read = True
        notification.save()
        return Response({'message': 'Notification marked as read'})
    except Notification.DoesNotExist:
        return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_all_notifications_read(request):
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return Response({'message': 'All notifications marked as read'})


class ChatMessageListView(generics.ListCreateAPIView):
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    ordering = ['-created_at']

    def get_queryset(self):
        return ChatMessage.objects.filter(
            sender=self.request.user
        ).union(
            ChatMessage.objects.filter(recipient=self.request.user)
        ).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)


class CustomerSupportTicketListView(generics.ListCreateAPIView):
    serializer_class = CustomerSupportTicketSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'priority']
    ordering = ['-created_at']

    def get_queryset(self):
        if self.request.user.is_admin or self.request.user.is_moderator:
            return CustomerSupportTicket.objects.all()
        else:
            return CustomerSupportTicket.objects.filter(customer=self.request.user)

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)


class CustomerSupportTicketDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = CustomerSupportTicketSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_admin or self.request.user.is_moderator:
            return CustomerSupportTicket.objects.all()
        else:
            return CustomerSupportTicket.objects.filter(customer=self.request.user)


class TicketMessageListView(generics.ListCreateAPIView):
    serializer_class = TicketMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    ordering = ['created_at']

    def get_queryset(self):
        ticket_id = self.kwargs['ticket_id']
        return TicketMessage.objects.filter(ticket_id=ticket_id)

    def perform_create(self, serializer):
        ticket_id = self.kwargs['ticket_id']
        serializer.save(ticket_id=ticket_id, sender=self.request.user)


class EmailTemplateListView(generics.ListCreateAPIView):
    queryset = EmailTemplate.objects.all()
    serializer_class = EmailTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_admin:
            return EmailTemplate.objects.all()
        return EmailTemplate.objects.filter(is_active=True)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def notification_dashboard(request):
    """Dashboard for moderators and admins"""
    if not (request.user.is_admin or request.user.is_moderator):
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    from django.db.models import Count
    
    stats = {
        'open_tickets': CustomerSupportTicket.objects.filter(status='open').count(),
        'in_progress_tickets': CustomerSupportTicket.objects.filter(status='in_progress').count(),
        'urgent_tickets': CustomerSupportTicket.objects.filter(priority='urgent').count(),
        'unread_messages': ChatMessage.objects.filter(is_read=False).count(),
    }
    
    return Response(stats)