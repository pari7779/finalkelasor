from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal

User = settings.AUTH_USER_MODEL

class Invoice(models.Model):
    """
    مدل فاکتور با تمام ویژگی‌های درخواستی
    """
    class Status(models.TextChoices):
        PENDING = 'pending', _('در انتظار پرداخت')
        PAID = 'paid', _('پرداخت شده')
        FAILED = 'failed', _('پرداخت ناموفق')
        CANCELED = 'canceled', _('لغو شده')

    class PaymentMethod(models.TextChoices):
        ONLINE = 'online', _('پرداخت آنلاین')
        OFFLINE = 'offline', _('پرداخت آفلاین')
        WALLET = 'wallet', _('کیف پول')

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='invoices',
        verbose_name=_('کاربر')
    )
    amount = models.DecimalField(
        _('مبلغ'),
        max_digits=12,
        decimal_places=0,
        validators=[MinValueValidator(Decimal('1000'))]
    )
    title = models.CharField(_('عنوان فاکتور'), max_length=100)
    description = models.TextField(_('توضیحات'), blank=True)
    status = models.CharField(
        _('وضعیت'),
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING
    )
    payment_method = models.CharField(
        _('روش پرداخت'),
        max_length=15,
        choices=PaymentMethod.choices,
        null=True,
        blank=True
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_invoices',
        verbose_name=_('ایجادکننده')
    )
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ بروزرسانی'), auto_now=True)

    # پرداخت آنلاین
    payment_gateway = models.CharField(_('درگاه پرداخت'), max_length=50, blank=True)
    payment_tracking_code = models.CharField(_('کد پیگیری پرداخت'), max_length=100, blank=True)

    # پرداخت آفلاین
    offline_receipt_image = models.ImageField(
        _('تصویر رسید پرداخت'),
        upload_to='finance/receipts/',
        null=True,
        blank=True
    )
    offline_receipt_code = models.CharField(_('کد پیگیری پرداخت آفلاین'), max_length=100, blank=True)
    offline_payment_date = models.DateField(_('تاریخ پرداخت آفلاین'), null=True, blank=True)

    class Meta:
        verbose_name = _('فاکتور')
        verbose_name_plural = _('فاکتورها')
        ordering = ['-created_at']

    def __str__(self):
        return f"فاکتور #{self.id} - {self.user} - {self.amount} تومان"

    def get_payment_type_display(self):
        if self.payment_method == self.PaymentMethod.ONLINE:
            return "پرداخت آنلاین"
        elif self.payment_method == self.PaymentMethod.OFFLINE:
            return "پرداخت آفلاین"
        return "نامشخص"

class Transaction(models.Model):
    """
    مدل تراکنش‌های مالی کاربران
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='transactions',
        verbose_name=_('کاربر')
    )
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='transactions',
        verbose_name=_('فاکتور'),
        null=True,
        blank=True
    )
    amount = models.DecimalField(
        _('مبلغ'),
        max_digits=12,
        decimal_places=0
    )
    transaction_type = models.CharField(
        _('نوع تراکنش'),
        max_length=20,
        choices=[
            ('payment', 'پرداخت'),
            ('charge', 'شارژ کیف پول'),
            ('refund', 'عودت وجه')
        ]
    )
    description = models.TextField(_('توضیحات'), blank=True)
    created_at = models.DateTimeField(_('تاریخ تراکنش'), auto_now_add=True)

    class Meta:
        verbose_name = _('تراکنش')
        verbose_name_plural = _('تراکنش‌ها')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.amount} تومان"
