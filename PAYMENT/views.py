from django.shortcuts import render

from django.db import models
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import Invoice, Transaction
from .serializers import (
    InvoiceListSerializer,
    InvoiceDetailSerializer,
    InvoiceCreateSerializer,
    OfflinePaymentSerializer,
    TransactionSerializer
)

class InvoiceViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Invoice.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return InvoiceListSerializer
        elif self.action == 'retrieve':
            return InvoiceDetailSerializer
        elif self.action == 'create':
            return InvoiceCreateSerializer
        elif self.action == 'offline_payment':
            return OfflinePaymentSerializer
        return InvoiceDetailSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        
        if user.is_staff:
            # پشتیبان‌ها همه فاکتورها را می‌بینند
            return queryset.select_related('user', 'created_by')
        else:
            # کاربران فقط فاکتورهای خودشان را می‌بینند
            return queryset.filter(user=user).select_related('user', 'created_by')

    def perform_create(self, serializer):
        if self.request.user.is_staff:
            serializer.save(created_by=self.request.user)
        else:
            serializer.save(user=self.request.user, created_by=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def pay_online(self, request, pk=None):
        """پرداخت آنلاین فاکتور"""
        invoice = self.get_object()
        
        if invoice.user != request.user:
            return Response(
                {'detail': 'شما فقط می‌توانید فاکتورهای خود را پرداخت کنید.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # اتصال به درگاه پرداخت (شبیه‌سازی شده)
        payment_data = {
            'status': 'success',
            'tracking_code': 'PAY' + str(timezone.now().timestamp()).replace('.', '')[:10],
            'gateway': 'زرین پال'
        }
        
        invoice.status = Invoice.Status.PAID
        invoice.payment_method = Invoice.PaymentMethod.ONLINE
        invoice.payment_tracking_code = payment_data['tracking_code']
        invoice.payment_gateway = payment_data['gateway']
        invoice.save()
        
        # ایجاد تراکنش
        Transaction.objects.create(
            user=request.user,
            invoice=invoice,
            amount=invoice.amount,
            transaction_type='payment',
            description=f'پرداخت آنلاین فاکتور #{invoice.id}'
        )
        
        return Response({
            'status': 'success',
            'message': 'پرداخت با موفقیت انجام شد.',
            'tracking_code': payment_data['tracking_code']
        })

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def offline_payment(self, request, pk=None):
        """ثبت پرداخت آفلاین"""
        invoice = self.get_object()
        
        if invoice.user != request.user:
            return Response(
                {'detail': 'شما فقط می‌توانید فاکتورهای خود را پرداخت کنید.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(invoice, data=request.data)
        serializer.is_valid(raise_exception=True)
        
        invoice.status = Invoice.Status.PAID
        invoice.payment_method = Invoice.PaymentMethod.OFFLINE
        invoice.offline_receipt_image = serializer.validated_data['offline_receipt_image']
        invoice.offline_receipt_code = serializer.validated_data['offline_receipt_code']
        invoice.offline_payment_date = serializer.validated_data['offline_payment_date']
        invoice.save()
        
        # ایجاد تراکنش
        Transaction.objects.create(
            user=request.user,
            invoice=invoice,
            amount=invoice.amount,
            transaction_type='payment',
            description=f'پرداخت آفلاین فاکتور #{invoice.id}'
        )
        
        return Response({
            'status': 'success',
            'message': 'رسید پرداخت با موفقیت ثبت شد.',
            'invoice_id': invoice.id
        })

class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Transaction.objects.all().select_related('user', 'invoice')
        return Transaction.objects.filter(user=user).select_related('invoice')

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """خلاصه وضعیت مالی کاربر"""
        user = request.user
        transactions = Transaction.objects.filter(user=user)
        
        total_payments = transactions.filter(transaction_type='payment').aggregate(
            total=models.Sum('amount')
        )['total'] or 0
        
        last_transactions = transactions.order_by('-created_at')[:5]
        
        return Response({
            'total_payments': total_payments,
            'last_transactions': TransactionSerializer(last_transactions, many=True).data
        })