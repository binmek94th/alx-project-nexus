from rest_framework.routers import DefaultRouter

from post.views import PostViewSet, LikeViewSet, CommentViewSet

router = DefaultRouter()

router.register(r'posts', PostViewSet, basename='posts')
router.register('likes', LikeViewSet, basename='like')
router.register(r'comments', CommentViewSet, basename='comment')

urlpatterns = router.urls
