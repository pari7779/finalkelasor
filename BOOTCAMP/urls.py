from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BootcampViewSet, BootcampRegistrationViewSet

router = DefaultRouter()
router.register(r'bootcamps', BootcampViewSet)
router.register(r'registrations', BootcampRegistrationViewSet, basename='registration')

urlpatterns = [
    path('', include(router.urls)),
]