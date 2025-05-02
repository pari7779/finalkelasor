from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.exceptions import ValidationError
from django.utils import timezone
import random
from datetime import timedelta

class CustomUserManager(BaseUserManager):
    def _create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError("شماره تلفن باید وارد شود")
        
        if self.model.objects.filter(phone=phone).exists():
            raise ValidationError("این شماره تلفن قبلا ثبت شده است")
            
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_user(self, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_support', False)
        return self._create_user(phone, password, **extra_fields)
    
    def create_support_user(self, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_support', True)
        return self._create_user(phone, password, **extra_fields)
    
    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_support', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('سوپریوزر باید is_staff=True باشد')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('سوپریوزر باید is_superuser=True باشد')
            
        return self._create_user(phone, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    USER_TYPE_CHOICES = [
        ('normal', 'کاربر عادی'),
        ('support', 'پشتیبان'),
        ('superuser', 'سوپریوزر'),
    ]
    
    phone = models.CharField(max_length=15, unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    national_id = models.CharField(max_length=10, unique=True)
    gender = models.CharField(max_length=10, choices=[('male', 'مرد'), ('female', 'زن')])
    is_staff = models.BooleanField(default=False)
    is_support = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='normal')
    otp = models.CharField(max_length=6, null=True, blank=True)
    otp_expiry = models.DateTimeField(null=True, blank=True)
    otp_retry_count = models.PositiveIntegerField(default=0)
    otp_last_sent = models.DateTimeField(null=True, blank=True)
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'national_id']
    
    def __str__(self):
        return f"{self.phone} - {self.get_full_name()}"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def generate_otp(self):
        self.otp = str(random.randint(100000, 999999))
        self.otp_expiry = timezone.now() + timedelta(minutes=5)
        self.otp_retry_count += 1
        self.otp_last_sent = timezone.now()
        self.save()
        return self.otp
    
    def can_resend_otp(self):
        if not self.otp_last_sent:
            return True
        return timezone.now() > self.otp_last_sent + timedelta(minutes=2)

class SupportPermission(models.Model):
    PERMISSION_CHOICES = [
        ('bootcamp', 'مدیریت بوتکمپ‌ها'),
        ('ticket', 'مدیریت تیکت‌ها'),
        ('blog', 'مدیریت بلاگ'),
        ('finance', 'مدیریت مالی'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='support_permissions')
    permission = models.CharField(max_length=20, choices=PERMISSION_CHOICES)
    
    class Meta:
        unique_together = ('user', 'permission')
    
    def __str__(self):
        return f"{self.user} - {self.get_permission_display()}"

class SMSLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    otp = models.CharField(max_length=6)
    status = models.CharField(max_length=20)
    response = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
