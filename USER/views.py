from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import RegisterSerializer, LoginSerializer, OTPSerializer, UserSerializer
from .models import User, SMSLog
from .services.sms_service import send_otp_via_kaveneghar
import random
from django.utils import timezone
from datetime import timedelta

MAX_OTP_RETRIES = 5
OTP_RETRY_TIMEOUT = timedelta(minutes=30)

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "user": UserSerializer(user).data,
            "message": "ثبت نام با موفقیت انجام شد"
        }, status=status.HTTP_201_CREATED)

class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

class SendOTPView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        phone = request.data.get('phone')
        
        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            return Response(
                {"detail": "کاربری با این شماره تلفن یافت نشد"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if user.otp_retry_count >= MAX_OTP_RETRIES:
            if timezone.now() < user.otp_last_sent + OTP_RETRY_TIMEOUT:
                return Response(
                    {"detail": "تعداد درخواست‌ها بیش از حد مجاز است. لطفاً 30 دقیقه دیگر تلاش کنید."},
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )
            else:
                user.otp_retry_count = 0
        
        if not user.can_resend_otp():
            return Response(
                {"detail": "لطفاً 2 دقیقه بعد مجدداً تلاش کنید"},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        
        otp = user.generate_otp()
        
        # ارسال OTP از طریق کاوهنگار
        success = send_otp_via_kaveneghar(phone, otp)
        
        # ذخیره لاگ ارسال
        SMSLog.objects.create(
            user=user,
            phone=phone,
            otp=otp,
            status='success' if success else 'failed',
            response={'manual_log': 'در حالت توسعه'}
        )
        
        if not success:
            return Response(
                {"detail": "خطا در ارسال کد تأیید"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return Response({
            "message": "کد تأیید به شماره شما ارسال شد",
            "expiry": "5 دقیقه",
            "retry_after": "2 دقیقه"
        }, status=status.HTTP_200_OK)

class VerifyOTPView(generics.GenericAPIView):
    serializer_class = OTPSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        user.otp = None
        user.otp_expiry = None
        user.save()
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            "user": UserSerializer(user).data,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "message": "ورود با موفقیت انجام شد"
        }, status=status.HTTP_200_OK)

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user
