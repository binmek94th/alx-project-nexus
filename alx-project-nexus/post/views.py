from rest_framework.pagination import CursorPagination
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from post.models import Post, Like, Comment
from post.serializers import PostSerializer, LikeSerializer, CommentSerializer, CommentListSerializer
from post.utils.handle_private import handle_private_posts
from post.utils.serialize_comments import build_comment_tree


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
        return handle_private_posts(user, Like, post_id)

    def perform_update(self, serializer):
        raise NotImplementedError

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context


class CommentViewSet(ModelViewSet):
    """
    ViewSet for managing comments on posts.
    This ViewSet provides CRUD operations for the Comment model.
    It allows users to create, retrieve, and update.
    The queryset only includes top-level comments (comments without a parent).
    Comments can have nested replies, which are prefetched for efficiency.
    The serializer used is CommentSerializer for individual comments and CommentListSerializer for listing comments.
    The get_queryset method filters comments based on the 'post_id' query parameter.
    If 'post_id' is provided, it retrieves comments for that post, checking the user's
    build_comment_tree function is used to build a tree structure of comments for better representation.
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get_queryset(self):
        post_id = self.request.query_params.get('post_id')
        user = self.request.user

        if post_id:
            return handle_private_posts(user, Comment, post_id).select_related('user', 'comment').order_by('created_at')

        else:
            return Comment.objects.filter(user=user)

    def list(self, request, *args, **kwargs):
        post_id = self.request.query_params.get('post_id')
        queryset = self.get_queryset()
        if post_id:
            queryset = build_comment_tree(list(queryset))
        else:
            queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context

    def get_serializer_class(self):
        post_id = self.request.query_params.get('post_id')
        if self.action == 'list' and post_id:
            return CommentListSerializer
        return CommentSerializer

    def perform_destroy(self, instance):
        raise NotImplementedError
