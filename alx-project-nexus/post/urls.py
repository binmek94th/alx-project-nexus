from rest_framework.routers import DefaultRouter

from post.views import PostViewSet

router = DefaultRouter()

router.register(r'posts', PostViewSet)

urlpatterns = router.urls
