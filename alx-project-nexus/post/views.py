from rest_framework.pagination import CursorPagination
from rest_framework.viewsets import ModelViewSet

from post.models import Post
from post.serializers import PostSerializer


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
