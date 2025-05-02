from rest_framework import permissions

class IsTicketOwnerOrSupport(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # برای پیام‌ها، چک می‌کنیم که کاربر مالک تیکت یا پشتیبان است
        if hasattr(obj, 'ticket'):
            ticket = obj.ticket
        else:
            ticket = obj
            
        return (
            request.user == ticket.user or 
            request.user.is_support
        )