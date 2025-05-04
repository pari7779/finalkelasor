from django.db import models   #تعریف مدل ها درجنگو
from django.contrib.auth import get_user_model  #دریافت مدل های کاربر که در پروژه استفاده میشود
from django.utils.translation import gettext_lazy as _  #قابلیت ترجمه ی عبارات
from django.utils.translation import gettext_lazy as _
User = get_user_model()
from django.core.exceptions import ValidationError  # روش صحیح برای مدل‌ها

class BootcampCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name="نام دسته‌بندی")
    description = models.TextField(blank=True, verbose_name="توضیحات")
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "دسته‌بندی بوتکمپ"
        verbose_name_plural = "دسته‌بندی‌های بوتکمپ"

class Bootcamp(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', _('پیش نویس')
        REGISTRATION = 'registration', _('در حال ثبت نام')
        ONGOING = 'ongoing', _('در حال برگزاری')
        COMPLETED = 'completed', _('برگزار شده')
        CANCELED = 'canceled', _('لغو شده')

    title = models.CharField(_('عنوان'), max_length=200)
    description = models.TextField(_('توضیحات'), blank=True)
    category = models.ForeignKey('BootcampCategory', on_delete=models.PROTECT, related_name='bootcamps')
    start_date = models.DateField(_('تاریخ شروع'))
    end_date = models.DateField(_('تاریخ پایان'))
    schedule_days = models.CharField(_('روزهای برگزاری'), max_length=100)
    schedule_time = models.CharField(_('ساعات برگزاری'), max_length=100)
    capacity = models.PositiveIntegerField(_('ظرفیت'))
    status = models.CharField(_('وضعیت'), max_length=20, choices=Status.choices, default=Status.DRAFT)
    is_advance = models.BooleanField(_('ادونس؟'), default=False)  # برای تفکیک بوتکمپ‌های ادونس/حضوری
    price = models.PositiveIntegerField(_('قیمت'), default=0)  # قیمت به تومان

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

    class Meta:
        verbose_name = _('بوتکمپ')
        verbose_name_plural = _('بوتکمپ‌ها')


class BootcampRegistration(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', _('بررسی نشده')
        REVIEWING = 'reviewing', _('در حال بررسی')
        APPROVED = 'approved', _('تایید شده')
        REJECTED = 'rejected', _('تایید نشده')

    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='bootcamp_registrations')
    bootcamp = models.ForeignKey('Bootcamp', on_delete=models.CASCADE, related_name='registrations')
    status = models.CharField(_('وضعیت'), max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(_('تاریخ ثبت‌نام'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ بروزرسانی'), auto_now=True)
    payment_receipt = models.ImageField(_('رسید پرداخت'), upload_to='receipts/', null=True, blank=True)  # برای پرداخت آفلاین

    def clean(self):
        if self.bootcamp.status != Bootcamp.Status.REGISTRATION:
            raise ValidationError(_('این بوتکمپ در حال ثبت‌نام نیست.'))

    class Meta:
        verbose_name = _('ثبت‌نام بوتکمپ')
        verbose_name_plural = _('ثبت‌نام‌های بوتکمپ')
        unique_together = ('user', 'bootcamp')


