from rest_framework import serializers
from .models import Invoice, Transaction
from django.contrib.auth import get_user_model

User = get_user_model()

class UserMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'phone', 'first_name', 'last_name']

class InvoiceListSerializer(serializers.ModelSerializer):
    user = UserMiniSerializer()
    status_display = serializers.CharField(source='get_status_display')
    payment_type = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = [
            'id', 'user', 'title', 'amount', 'status', 
            'status_display', 'payment_type', 'created_at'
        ]

    def get_payment_type(self, obj):
        return obj.get_payment_type_display()

class InvoiceDetailSerializer(serializers.ModelSerializer):
    user = UserMiniSerializer()
    created_by = UserMiniSerializer()
    status_display = serializers.CharField(source='get_status_display')
    payment_type = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = '__all__'

    def get_payment_type(self, obj):
        return obj.get_payment_type_display()

class InvoiceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = ['user', 'title', 'amount', 'description']
        extra_kwargs = {
            'user': {'required': True}
        }

class OfflinePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = [
            'offline_receipt_image', 
            'offline_receipt_code',
            'offline_payment_date'
        ]
        extra_kwargs = {
            'offline_receipt_image': {'required': True},
            'offline_receipt_code': {'required': True},
            'offline_payment_date': {'required': True}
        }

class TransactionSerializer(serializers.ModelSerializer):
    invoice = serializers.StringRelatedField()

    class Meta:
        model = Transaction
        fields = [
            'id', 'invoice', 'amount', 
            'transaction_type', 'description', 'created_at'
        ]