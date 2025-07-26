from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from user.models import Follow


class FollowerViewSet(ModelViewSet):
    """
    A viewset for viewing and editing follower instances.
    """
    queryset = Follow.objects.all()
    serializer_class = FollowerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Follow.objects.filter(following=user)
