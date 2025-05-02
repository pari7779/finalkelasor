from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import Bootcamp
from .serializers import BootcampSerializer
from .permissions import IsSuperUserOrReadOnly

class BootcampViewSet(viewsets.ModelViewSet):
    queryset = Bootcamp.objects.all()
    serializer_class = BootcampSerializer
    permission_classes = [IsSuperUserOrReadOnly]  # فقط سوپریوزر می‌تواند ویرایش کند

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.query_params.get('status'):
            queryset = queryset.filter(status=self.request.query_params.get('status'))
        return queryset
    
    from rest_framework.response import Response
from rest_framework.decorators import action

class BootcampRegistrationViewSet(viewsets.ModelViewSet):
    serializer_class = BootcampRegistrationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return BootcampRegistration.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def approve(self, request, pk=None):
        registration = self.get_object()
        registration.status = BootcampRegistration.Status.APPROVED
        registration.save()
        # ارسال نوتیفیکیشن به کاربر (با Celery)
        return Response({'status': 'approved'})
    
    
