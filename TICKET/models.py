from django.db import models
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

class Ticket(models.Model):
    STATUS_CHOICES = [
        ('under_review', 'درحال بررسی'),
        ('answered', 'پاسخ داده شده'),
        ('unanswered', 'پاسخ داده نشده'),
        ('closed', 'بسته شده'),
    ]
    
    user = models.ForeignKey(
        'User', 
        on_delete=models.CASCADE,
        related_name='tickets'
    )
    bootcamp = models.ForeignKey(
        'bootcamp.Bootcamp',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    subject = models.CharField(max_length=200)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='under_review'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        is_new = not self.pk
        super().save(*args, **kwargs)
        
        if is_new:
            self._notify_support_team()

    def _notify_support_team(self):
        subject = f"تیکت جدید #{self.id}: {self.subject}"
        message = render_to_string('tickets/email/new_ticket_notification.txt', {
            'ticket': self,
            'user': self.user
        })
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.SUPPORT_EMAIL],
            fail_silently=False,
        )

class TicketMessage(models.Model):
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        'User',
        on_delete=models.CASCADE
    )
    content = models.TextField()
    attachment = models.FileField(
        upload_to='ticket_attachments/%Y/%m/%d/',
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_from_support = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.is_from_support = self.sender.is_support
        super().save(*args, **kwargs)
        
        if not self.is_from_support:
            self._update_ticket_status()
        else:
            self._notify_user_reply()

    def _update_ticket_status(self):
        self.ticket.status = 'unanswered'
        self.ticket.save()

    def _notify_user_reply(self):
        subject = f"پاسخ به تیکت #{self.ticket.id}"
        message = render_to_string('tickets/email/support_reply_notification.txt', {
            'ticket': self.ticket,
            'message': self
        })
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [self.ticket.user.email],
            fail_silently=False,
        )