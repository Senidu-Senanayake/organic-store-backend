from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('order_confirmed', 'Order Confirmed'),
        ('order_shipped', 'Order Shipped'),
        ('order_delivered', 'Order Delivered'),
        ('order_cancelled', 'Order Cancelled'),
        ('low_stock', 'Low Stock Alert'),
        ('restock', 'Product Restocked'),
        ('new_message', 'New Message'),
        ('promotional', 'Promotional Offer'),
        ('system', 'System Notification'),
    )

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    is_sent = models.BooleanField(default=False)
    
    # Optional related objects
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, null=True, blank=True)
    
    # Delivery channels
    send_email = models.BooleanField(default=True)
    send_sms = models.BooleanField(default=False)
    send_push = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.recipient.username}: {self.title}"


class ChatMessage(models.Model):
    MESSAGE_TYPES = (
        ('customer_support', 'Customer Support'),
        ('order_inquiry', 'Order Inquiry'),
        ('product_question', 'Product Question'),
        ('general', 'General'),
    )

    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='general')
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    
    # Optional related objects
    order = models.ForeignKey('orders.Order', on_delete=models.SET_NULL, null=True, blank=True)
    product = models.ForeignKey('products.Product', on_delete=models.SET_NULL, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Message from {self.sender.username} to {self.recipient.username}"


class CustomerSupportTicket(models.Model):
    STATUS_CHOICES = (
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    )

    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    )

    ticket_number = models.CharField(max_length=20, unique=True, editable=False)
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='support_tickets')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets')
    
    subject = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    
    # Optional related objects
    order = models.ForeignKey('orders.Order', on_delete=models.SET_NULL, null=True, blank=True)
    product = models.ForeignKey('products.Product', on_delete=models.SET_NULL, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Ticket {self.ticket_number} - {self.subject}"

    def save(self, *args, **kwargs):
        if not self.ticket_number:
            self.ticket_number = self.generate_ticket_number()
        super().save(*args, **kwargs)

    def generate_ticket_number(self):
        import datetime
        import uuid
        now = datetime.datetime.now()
        return f"TKT{now.strftime('%Y%m%d')}{str(uuid.uuid4())[:6].upper()}"


class TicketMessage(models.Model):
    ticket = models.ForeignKey(CustomerSupportTicket, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_internal = models.BooleanField(default=False)  # Internal notes for staff
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Message in {self.ticket.ticket_number} by {self.sender.username}"


class EmailTemplate(models.Model):
    TEMPLATE_TYPES = (
        ('order_confirmation', 'Order Confirmation'),
        ('order_shipped', 'Order Shipped'),
        ('order_delivered', 'Order Delivered'),
        ('password_reset', 'Password Reset'),
        ('welcome', 'Welcome Email'),
        ('newsletter', 'Newsletter'),
        ('promotional', 'Promotional Email'),
    )

    name = models.CharField(max_length=100)
    template_type = models.CharField(max_length=30, choices=TEMPLATE_TYPES)
    subject = models.CharField(max_length=200)
    html_content = models.TextField()
    text_content = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.get_template_type_display()}"