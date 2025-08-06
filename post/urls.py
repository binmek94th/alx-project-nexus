from rest_framework.routers import DefaultRouter

from post.views import PostViewSet, LikeViewSet, CommentViewSet, StoryViewSet, StoryLikeViewSet

router = DefaultRouter()

router.register(r'posts', PostViewSet, basename='posts')
router.register('likes', LikeViewSet, basename='like')
router.register('story_likes', StoryLikeViewSet, basename='story_like')
router.register(r'comments', CommentViewSet, basename='comment')
router.register('stories', StoryViewSet, basename='stories')

urlpatterns = router.urls
