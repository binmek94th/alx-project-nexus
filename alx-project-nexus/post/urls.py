from rest_framework.routers import DefaultRouter

from post.views import PostViewSet, LikeViewSet

router = DefaultRouter()

router.register(r'posts', PostViewSet, basename='posts')
router.register('likes', LikeViewSet, basename='like')

urlpatterns = router.urls
