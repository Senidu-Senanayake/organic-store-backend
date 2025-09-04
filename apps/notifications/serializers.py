from rest_framework import serializers
from .models import Notification, ChatMessage, CustomerSupportTicket, TicketMessage, EmailTemplate


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ('recipient', 'is_sent', 'sent_at')


class ChatMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.username', read_only=True)
    recipient_name = serializers.CharField(source='recipient.username', read_only=True)

    class Meta:
        model = ChatMessage
        fields = '__all__'
        read_only_fields = ('sender',)


class TicketMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.username', read_only=True)

    class Meta:
        model = TicketMessage
        fields = '__all__'
        read_only_fields = ('sender',)


class CustomerSupportTicketSerializer(serializers.ModelSerializer):
    messages = TicketMessageSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source='customer.username', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.username', read_only=True)

    class Meta:
        model = CustomerSupportTicket
        fields = '__all__'
        read_only_fields = ('customer', 'ticket_number')


class EmailTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailTemplate
        fields = '__all__'