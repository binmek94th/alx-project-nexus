from rest_framework.routers import DefaultRouter

from post.views import PostViewSet, BaseLikeViewSet, CommentViewSet, StoryViewSet

router = DefaultRouter()

router.register(r'posts', PostViewSet, basename='posts')
router.register('likes', BaseLikeViewSet, basename='like')
router.register(r'comments', CommentViewSet, basename='comment')
router.register('stories', StoryViewSet, basename='stories')

urlpatterns = router.urls
