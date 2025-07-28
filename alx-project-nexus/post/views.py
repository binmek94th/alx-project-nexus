from rest_framework.pagination import CursorPagination
from rest_framework.viewsets import ModelViewSet

from post.models import Post, Like
from post.serializers import PostSerializer, LikeSerializer
from user.models import Follow


class PostViewSet(ModelViewSet):
    """
    ViewSet for managing posts.
    This ViewSet provides CRUD operations for the Post model.
    It allows users to create, retrieve, update, and delete posts.
    Posts can be filtered by hashtags using the 'hashtag' query parameter.
    The queryset only includes posts that are not marked as deleted.
    The serializer used is PostSerializer, which handles the serialization and deserialization of Post instances.
    """
    queryset = Post.objects.filter(is_deleted=False)
    serializer_class = PostSerializer
    pagination_class = CursorPagination

    ordering = ['-created_at']

    def get_queryset(self):
        hashtag = self.request.query_params.get('hashtag')
        if hashtag:
            return (Post.objects.prefetch_related('hashtags').filter(hashtags__name__iexact=hashtag)
                    .filter(is_deleted=False))
        return Post.objects.prefetch_related('hashtags').filter(is_deleted=False)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class LikeViewSet(ModelViewSet):
    """
    ViewSet for managing likes on posts.
    This ViewSet provides operations to like and unlike posts.
    It allows users to like a post by sending a POST request with the post ID.
    Users can also remove their like by sending a DELETE request with the post ID.
    The queryset only includes likes made by the authenticated user on public posts.
    The serializer used is LikeSerializer, which handles the serialization and deserialization of Like instances.
    The perform_update method is overridden to raise NotImplementedError, as likes cannot be updated.
    The get_serializer_context method is overridden to include the user in the context.
    if the 'post_id' query parameter is provided, it filters likes for that specific post.
    if the author is private, it checks if the user is following the author before returning likes.
    If not provided, it returns all likes made by the user.
    """
    queryset = Like.objects.all()
    serializer_class = LikeSerializer

    def get_queryset(self):
        post_id = self.request.query_params.get('post_id')
        user = self.request.user

        if post_id:
            try:
                post = Post.objects.select_related('author').get(id=post_id)
            except Post.DoesNotExist:
                return Like.objects.none()

            is_following = Follow.objects.filter(follower=user, following=post.author).exists()

            if post.author.privacy_choice == "public" or post.author == user or is_following:
                return Like.objects.filter(post_id=post_id)
            else:
                return Like.objects.none()
        return Like.objects.filter(user=user)

    def perform_update(self, serializer):
        raise NotImplementedError

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context
