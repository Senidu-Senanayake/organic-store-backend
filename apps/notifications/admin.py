from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Notification, ChatMessage, CustomerSupportTicket, 
    TicketMessage, EmailTemplate
)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'notification_type', 'title', 'is_read', 
                   'is_sent', 'created_at', 'notification_actions')
    list_filter = ('notification_type', 'is_read', 'is_sent', 'send_email', 
                  'send_sms', 'send_push', 'created_at')
    search_fields = ('recipient__username', 'title', 'message')
    list_editable = ('is_read', 'is_sent')
    readonly_fields = ('created_at', 'sent_at', 'read_at')
    
    fieldsets = (
        ('Notification Details', {
            'fields': ('recipient', 'notification_type', 'title', 'message')
        }),
        ('Related Objects', {
            'fields': ('order', 'product')
        }),
        ('Delivery Channels', {
            'fields': ('send_email', 'send_sms', 'send_push')
        }),
        ('Status', {
            'fields': ('is_read', 'is_sent')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'sent_at', 'read_at'),
            'classes': ('collapse',)
        })
    )
    
    def notification_actions(self, obj):
        actions = []
        if not obj.is_sent:
            actions.append('<a class="button" href="{}">Send Now</a>'.format(
                f'/admin/notifications/notification/{obj.pk}/change/?action=send'
            ))
        if not obj.is_read:
            actions.append('<a class="button" href="{}">Mark Read</a>'.format(
                f'/admin/notifications/notification/{obj.pk}/change/?action=read'
            ))
        return format_html(' '.join(actions))
    notification_actions.short_description = 'Actions'


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'message_type', 'subject', 
                   'is_read', 'created_at')
    list_filter = ('message_type', 'is_read', 'created_at')
    search_fields = ('sender__username', 'recipient__username', 'subject', 'message')
    readonly_fields = ('created_at', 'read_at')
    
    fieldsets = (
        ('Message Details', {
            'fields': ('sender', 'recipient', 'message_type', 'subject', 'message')
        }),
        ('Related Objects', {
            'fields': ('order', 'product')
        }),
        ('Status', {
            'fields': ('is_read',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'read_at'),
            'classes': ('collapse',)
        })
    )


class TicketMessageInline(admin.TabularInline):
    model = TicketMessage
    extra = 0
    readonly_fields = ('created_at',)
    fields = ('sender', 'message', 'is_internal', 'created_at')


@admin.register(CustomerSupportTicket)
class CustomerSupportTicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_number', 'customer', 'subject', 'status', 'priority', 
                   'assigned_to', 'created_at', 'ticket_actions')
    list_filter = ('status', 'priority', 'assigned_to', 'created_at', 'updated_at')
    search_fields = ('ticket_number', 'customer__username', 'subject', 'description')
    list_editable = ('status', 'priority', 'assigned_to')
    readonly_fields = ('ticket_number', 'created_at', 'updated_at', 'resolved_at')
    inlines = [TicketMessageInline]
    
    fieldsets = (
        ('Ticket Information', {
            'fields': ('ticket_number', 'customer', 'subject', 'description')
        }),
        ('Status & Assignment', {
            'fields': ('status', 'priority', 'assigned_to')
        }),
        ('Related Objects', {
            'fields': ('order', 'product')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'resolved_at'),
            'classes': ('collapse',)
        })
    )
    
    def ticket_actions(self, obj):
        actions = []
        if obj.status == 'open':
            actions.append('<a class="button" href="{}">Assign to Me</a>'.format(
                f'/admin/notifications/customersupportticket/{obj.pk}/change/?action=assign'
            ))
        if obj.status in ['open', 'in_progress']:
            actions.append('<a class="button" href="{}">Resolve</a>'.format(
                f'/admin/notifications/customersupportticket/{obj.pk}/change/?action=resolve'
            ))
        return format_html(' '.join(actions))
    ticket_actions.short_description = 'Actions'


@admin.register(TicketMessage)
class TicketMessageAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'sender', 'message_preview', 'is_internal', 'created_at')
    list_filter = ('is_internal', 'created_at', 'sender')
    search_fields = ('ticket__ticket_number', 'sender__username', 'message')
    readonly_fields = ('created_at',)
    
    def message_preview(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'Message Preview'


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'template_type', 'subject', 'is_active', 'created_at')
    list_filter = ('template_type', 'is_active', 'created_at')
    search_fields = ('name', 'subject', 'html_content')
    list_editable = ('is_active',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Template Information', {
            'fields': ('name', 'template_type', 'subject')
        }),
        ('Content', {
            'fields': ('html_content', 'text_content')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )