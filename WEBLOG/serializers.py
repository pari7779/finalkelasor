from rest_framework import serializers
from .models import BlogCategory, BlogTag, BlogPost, BlogComment, BlogLike
from django.contrib.auth import get_user_model

User = get_user_model()

class BlogCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogCategory
        fields = ['id', 'title', 'slug', 'created_at']
        read_only_fields = ['id', 'slug', 'created_at']

class BlogTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogTag
        fields = ['id', 'name', 'slug']
        read_only_fields = ['id', 'slug']

class BlogPostListSerializer(serializers.ModelSerializer):
    category = BlogCategorySerializer(read_only=True)
    tags = BlogTagSerializer(many=True, read_only=True)
    author = serializers.StringRelatedField()
    like_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'slug', 'excerpt', 'category', 'tags',
            'author', 'status', 'featured_image', 'published_at',
            'created_at', 'view_count', 'like_count', 'comment_count'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'published_at', 'view_count']

    def get_like_count(self, obj):
        return obj.likes.count()

    def get_comment_count(self, obj):
        return obj.comments.count()

class BlogPostDetailSerializer(BlogPostListSerializer):
    content = serializers.SerializerMethodField()

    class Meta(BlogPostListSerializer.Meta):
        fields = BlogPostListSerializer.Meta.fields + ['content', 'updated_at']
    
    def get_content(self, obj):
        return obj.content if obj.status == BlogPost.Status.PUBLISHED else None

class BlogPostCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogPost
        fields = [
            'title', 'content', 'excerpt', 'category', 'tags',
            'status', 'featured_image'
        ]

    def validate(self, data):
        if data.get('status') == BlogPost.Status.PUBLISHED and not data.get('content'):
            raise serializers.ValidationError(
                "برای انتشار مقاله، محتوا الزامی است."
            )
        return data

class BlogCommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()
    replies = serializers.SerializerMethodField()

    class Meta:
        model = BlogComment
        fields = [
            'id', 'author', 'content', 'is_approved',
            'created_at', 'updated_at', 'replies'
        ]
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']

    def get_replies(self, obj):
        if obj.replies.exists():
            return BlogCommentSerializer(obj.replies.all(), many=True).data
        return None

class BlogCommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogComment
        fields = ['content', 'parent']

class BlogLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogLike
        fields = ['id', 'user', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']