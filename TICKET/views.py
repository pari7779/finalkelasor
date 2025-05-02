
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Ticket, TicketMessage
from .serializers import TicketSerializer, TicketMessageSerializer, CreateTicketSerializer
from .permissions import IsTicketOwnerOrSupport

class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateTicketSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        user = self.request.user
        if user.is_support:
            return self.queryset
        return self.queryset.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsTicketOwnerOrSupport])
    def close(self, request, pk=None):
        ticket = self.get_object()
        ticket.status = 'closed'
        ticket.save()
        return Response({'status': 'تیکت با موفقیت بسته شد'})

class TicketMessageViewSet(viewsets.ModelViewSet):
    serializer_class = TicketMessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsTicketOwnerOrSupport]

    def get_queryset(self):
        return TicketMessage.objects.filter(ticket_id=self.kwargs['ticket_pk'])

    def perform_create(self, serializer):
        ticket = Ticket.objects.get(pk=self.kwargs['ticket_pk'])
        user = self.request.user
        
        if user.is_support:
            ticket.status = 'answered'
            ticket.save()
        
        serializer.save(
            sender=user,
            ticket=ticket,
            is_from_support=user.is_support
        )