from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TicketViewSet, TicketMessageViewSet

router = DefaultRouter()
router.register(r'tickets', TicketViewSet)
router.register(r'tickets/(?P<ticket_pk>\d+)/messages', TicketMessageViewSet, basename='ticket-message')

urlpatterns = [
    path('', include(router.urls)),
]