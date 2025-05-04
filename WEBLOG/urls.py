from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'categories', views.BlogCategoryViewSet, basename='blogcategory')
router.register(r'tags', views.BlogTagViewSet, basename='blogtag')
router.register(r'posts', views.BlogPostViewSet, basename='blogpost')

urlpatterns = [
    path('', include(router.urls)),
    path('posts/<slug:post_slug>/comments/', views.BlogCommentViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='blogcomment-list'),
    path('posts/<slug:post_slug>/comments/<int:pk>/', views.BlogCommentViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='blogcomment-detail'),
    path('posts/<slug:post_slug>/likes/', views.BlogLikeViewSet.as_view({
        'get': 'list',
        'post': 'create',
        'delete': 'destroy'
    }), name='bloglke-list'),
]