from django.contrib import admin
from .models import BlogCategory, BlogTag, BlogPost, BlogComment, BlogLike

@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'created_at']
    search_fields = ['title']
    prepopulated_fields = {'slug': ('title',)}

@admin.register(BlogTag)
class BlogTagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'author', 'published_at', 'view_count']
    list_filter = ['status', 'category', 'tags', 'published_at']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ['author', 'category', 'tags']
    date_hierarchy = 'published_at'
    ordering = ['-published_at']
    filter_horizontal = ['tags']

@admin.register(BlogComment)
class BlogCommentAdmin(admin.ModelAdmin):
    list_display = ['post', 'author', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'post']
    search_fields = ['content', 'author__phone']
    raw_id_fields = ['post', 'author', 'parent']

@admin.register(BlogLike)
class BlogLikeAdmin(admin.ModelAdmin):
    list_display = ['post', 'user', 'created_at']
    raw_id_fields = ['post', 'user']
