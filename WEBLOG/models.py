from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.conf import settings
import random

# استفاده از مدل کاربری فعلی شما بدون نیاز به تغییر
User = settings.AUTH_USER_MODEL

class BlogCategory(models.Model):
    """
    مدل دسته‌بندی مقالات وبلاگ
    """
    title = models.CharField(_("عنوان"), max_length=100)
    slug = models.SlugField(_("اسلاگ"), max_length=100, unique=True)
    created_at = models.DateTimeField(_("تاریخ ایجاد"), auto_now_add=True)
    updated_at = models.DateTimeField(_("تاریخ بروزرسانی"), auto_now=True)

    class Meta:
        verbose_name = _("دسته‌بندی وبلاگ")
        verbose_name_plural = _("دسته‌بندی‌های وبلاگ")

    def __str__(self):
        return self.title

class BlogTag(models.Model):
    """
    مدل تگ‌های مقالات
    """
    name = models.CharField(_("نام تگ"), max_length=50, unique=True)
    slug = models.SlugField(_("اسلاگ"), max_length=50, unique=True)

    class Meta:
        verbose_name = _("تگ وبلاگ")
        verbose_name_plural = _("تگ‌های وبلاگ")

    def __str__(self):
        return self.name

class BlogPost(models.Model):
    """
    مدل اصلی مقالات وبلاگ
    """
    class Status(models.TextChoices):
        DRAFT = 'draft', _('پیش نویس')
        PUBLISHED = 'published', _('منتشر شده')

    title = models.CharField(_("عنوان"), max_length=200)
    slug = models.SlugField(_("اسلاگ"), max_length=200, unique=True)
    content = models.TextField(_("محتوا"))
    excerpt = models.TextField(_("چکیده"), max_length=300, blank=True)
    category = models.ForeignKey(
        BlogCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts',
        verbose_name=_("دسته‌بندی")
    )
    tags = models.ManyToManyField(
        BlogTag,
        blank=True,
        related_name='posts',
        verbose_name=_("تگ‌ها")
    )
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='blog_posts',
        verbose_name=_("نویسنده")
    )
    status = models.CharField(
        _("وضعیت"),
        max_length=10,
        choices=Status.choices,
        default=Status.DRAFT
    )
    featured_image = models.ImageField(
        _("تصویر شاخص"),
        upload_to='blog/featured_images/',
        null=True,
        blank=True
    )
    published_at = models.DateTimeField(_("تاریخ انتشار"), null=True, blank=True)
    created_at = models.DateTimeField(_("تاریخ ایجاد"), auto_now_add=True)
    updated_at = models.DateTimeField(_("تاریخ بروزرسانی"), auto_now=True)
    view_count = models.PositiveIntegerField(_("تعداد بازدید"), default=0)

    class Meta:
        verbose_name = _("مقاله وبلاگ")
        verbose_name_plural = _("مقالات وبلاگ")
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.status == self.Status.PUBLISHED and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def increase_view_count(self):
        self.view_count += 1
        self.save(update_fields=['view_count'])

class BlogComment(models.Model):
    """
    مدل نظرات مقالات
    """
    post = models.ForeignKey(
        BlogPost,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name=_("مقاله")
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='blog_comments',
        verbose_name=_("نویسنده نظر")
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        verbose_name=_("پاسخ به")
    )
    content = models.TextField(_("متن نظر"))
    is_approved = models.BooleanField(_("تایید شده"), default=False)
    created_at = models.DateTimeField(_("تاریخ ایجاد"), auto_now_add=True)
    updated_at = models.DateTimeField(_("تاریخ بروزرسانی"), auto_now=True)

    class Meta:
        verbose_name = _("نظر وبلاگ")
        verbose_name_plural = _("نظرات وبلاگ")
        ordering = ['-created_at']

    def __str__(self):
        return f"نظر {self.author} برای مقاله {self.post.title}"

class BlogLike(models.Model):
    """
    مدل لایک‌های مقالات
    """
    post = models.ForeignKey(
        BlogPost,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name=_("مقاله")
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='blog_likes',
        verbose_name=_("کاربر")
    )
    created_at = models.DateTimeField(_("تاریخ ایجاد"), auto_now_add=True)

    class Meta:
        verbose_name = _("لایک وبلاگ")
        verbose_name_plural = _("لایک‌های وبلاگ")
        unique_together = ('post', 'user')

    def __str__(self):
        return f"لایک {self.user} برای مقاله {self.post.title}"