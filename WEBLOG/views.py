from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Count

from .models import BlogCategory, BlogTag, BlogPost, BlogComment, BlogLike
from .serializers import (
    BlogCategorySerializer,
    BlogTagSerializer,
    BlogPostListSerializer,
    BlogPostDetailSerializer,
    BlogPostCreateUpdateSerializer,
    BlogCommentSerializer,
    BlogCommentCreateSerializer,
    BlogLikeSerializer
)

class BlogCategoryViewSet(viewsets.ModelViewSet):
    queryset = BlogCategory.objects.all()
    serializer_class = BlogCategorySerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'slug'

class BlogTagViewSet(viewsets.ModelViewSet):
    queryset = BlogTag.objects.all()
    serializer_class = BlogTagSerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'slug'

class BlogPostViewSet(viewsets.ModelViewSet):
    queryset = BlogPost.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action == 'list':
            return BlogPostListSerializer
        elif self.action == 'retrieve':
            return BlogPostDetailSerializer
        return BlogPostCreateUpdateSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(status=BlogPost.Status.PUBLISHED)
        
        # فیلتر بر اساس دسته‌بندی
        category_slug = self.request.query_params.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # فیلتر بر اساس تگ
        tag_slug = self.request.query_params.get('tag')
        if tag_slug:
            queryset = queryset.filter(tags__slug=tag_slug)
        
        # فیلتر بر اساس نویسنده
        author_id = self.request.query_params.get('author')
        if author_id:
            queryset = queryset.filter(author__id=author_id)
        
        return queryset.annotate(
            like_count=Count('likes'),
            comment_count=Count('comments')
        )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def publish(self, request, slug=None):
        post = self.get_object()
        post.status = BlogPost.Status.PUBLISHED
        post.published_at = timezone.now()
        post.save()
        return Response({'status': 'مقاله منتشر شد.'})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def unpublish(self, request, slug=None):
        post = self.get_object()
        post.status = BlogPost.Status.DRAFT
        post.save()
        return Response({'status': 'مقاله به پیش نویس تغییر یافت.'})

    @action(detail=True, methods=['get'])
    def view(self, request, slug=None):
        post = self.get_object()
        post.increase_view_count()
        return Response({'view_count': post.view_count})

class BlogCommentViewSet(viewsets.ModelViewSet):
    serializer_class = BlogCommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return BlogComment.objects.filter(
            post__slug=self.kwargs['post_slug'],
            is_approved=True,
            parent__isnull=True
        )

    def get_serializer_class(self):
        if self.action in ['create', 'update']:
            return BlogCommentCreateSerializer
        return BlogCommentSerializer

    def perform_create(self, serializer):
        post = get_object_or_404(BlogPost, slug=self.kwargs['post_slug'])
        serializer.save(
            author=self.request.user,
            post=post
        )

class BlogLikeViewSet(viewsets.ModelViewSet):
    serializer_class = BlogLikeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return BlogLike.objects.filter(
            post__slug=self.kwargs['post_slug'],
            user=self.request.user
        )

    def perform_create(self, serializer):
        post = get_object_or_404(BlogPost, slug=self.kwargs['post_slug'])
        if BlogLike.objects.filter(post=post, user=self.request.user).exists():
            return Response(
                {'detail': 'شما قبلاً این مقاله را لایک کرده‌اید.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer.save(user=self.request.user, post=post)
