from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.utils import timezone
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'phone', 'first_name', 'last_name', 'national_id', 'gender', 'user_type']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['phone', 'password', 'first_name', 'last_name', 'national_id', 'gender']
    
    def create(self, validated_data):
        user = User.objects.create_user(
            phone=validated_data['phone'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            national_id=validated_data['national_id'],
            gender=validated_data['gender']
        )
        return user

class LoginSerializer(serializers.Serializer):
    phone = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        phone = attrs.get('phone')
        password = attrs.get('password')
        
        user = authenticate(phone=phone, password=password)
        
        if not user:
            raise serializers.ValidationError('شماره تلفن یا رمز عبور اشتباه است')
        
        if not user.is_active:
            raise serializers.ValidationError('حساب کاربری غیرفعال است')
        
        refresh = RefreshToken.for_user(user)
        
        return {
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

class OTPSerializer(serializers.Serializer):
    phone = serializers.CharField()
    otp = serializers.CharField(max_length=6)

    def validate(self, attrs):
        phone = attrs.get('phone')
        otp = attrs.get('otp')
        
        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            raise serializers.ValidationError('کاربری با این شماره تلفن یافت نشد')
        
        if user.otp != otp:
            raise serializers.ValidationError('کد تأیید نامعتبر است')
        
        if user.otp_expiry < timezone.now():
            raise serializers.ValidationError('کد تأیید منقضی شده است')
        
        attrs['user'] = user
        return attrs