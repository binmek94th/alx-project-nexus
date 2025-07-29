from rest_framework.routers import DefaultRouter

from notification.views import NotificationViewSet

router = DefaultRouter()

router.register(r'notifications', NotificationViewSet)

urlpatterns = router.urls
