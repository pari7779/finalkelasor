from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'invoices', views.InvoiceViewSet, basename='invoice')
router.register(r'transactions', views.TransactionViewSet, basename='transaction')

urlpatterns = [
    path('', include(router.urls)),
    path('invoices/<int:pk>/pay-online/', views.InvoiceViewSet.as_view({'post': 'pay_online'}), name='invoice-pay-online'),
    path('invoices/<int:pk>/offline-payment/', views.InvoiceViewSet.as_view({'post': 'offline_payment'}), name='invoice-offline-payment'),
    path('transactions/summary/', views.TransactionViewSet.as_view({'get': 'summary'}), name='transaction-summary'),
]