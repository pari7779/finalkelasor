from rest_framework import serializers
from .models import Ticket, TicketMessage

class TicketMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.get_full_name', read_only=True)
    sender_type = serializers.SerializerMethodField()

    class Meta:
        model = TicketMessage
        fields = [
            'id', 'sender', 'sender_name', 'sender_type',
            'content', 'attachment', 'created_at', 'is_from_support'
        ]
        read_only_fields = ['sender', 'created_at', 'is_from_support']

    def get_sender_type(self, obj):
        return 'پشتیبان' if obj.is_from_support else 'کاربر'

class TicketSerializer(serializers.ModelSerializer):
    messages = TicketMessageSerializer(many=True, read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    bootcamp_title = serializers.CharField(source='bootcamp.title', read_only=True, allow_null=True)

    class Meta:
        model = Ticket
        fields = [
            'id', 'user', 'user_name', 'bootcamp', 'bootcamp_title',
            'subject', 'status', 'messages', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'status', 'created_at', 'updated_at']

class CreateTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['subject', 'bootcamp']
        extra_kwargs = {
            'bootcamp': {'required': False}
        }

    def validate_bootcamp(self, value):
        if value and not self.context['request'].user.registered_bootcamps.filter(id=value.id).exists():
            raise serializers.ValidationError("شما در این بوتکمپ ثبت‌نام نکرده‌اید")
        return value