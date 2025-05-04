from django.contrib import admin
from django.contrib import admin
from .models import Invoice, Transaction

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'title', 'amount', 'status', 'payment_method', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['user__phone', 'title', 'payment_tracking_code']
    raw_id_fields = ['user', 'created_by']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    actions = ['mark_as_paid', 'mark_as_pending']

    def mark_as_paid(self, request, queryset):
        queryset.update(status='paid')
    mark_as_paid.short_description = "تغییر وضعیت به پرداخت شده"

    def mark_as_pending(self, request, queryset):
        queryset.update(status='pending')
    mark_as_pending.short_description = "تغییر وضعیت به در انتظار پرداخت"

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'amount', 'transaction_type', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['user__phone', 'invoice__id']
    raw_id_fields = ['user', 'invoice']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']