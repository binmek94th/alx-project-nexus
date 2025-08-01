from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from notification.models import Notification
from notification.serializers import NotificationSerializer


class NotificationViewSet(ModelViewSet):
    """
    API endpoint that allows notifications to be viewed or edited.
    the user should be authenticated.
    the perform_create method is overridden, to stop creation of notifications manualy.
    """
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Notification.objects.filter(user=user).order_by('-created_at')

    def perform_create(self, serializer):
        raise NotImplementedError

    def perform_destroy(self, instance):
        raise NotImplementedError
