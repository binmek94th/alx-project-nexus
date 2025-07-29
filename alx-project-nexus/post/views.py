from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import CursorPagination
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from post.models import Post, Comment, Story
from post.serializers import PostSerializer, LikeSerializer, CommentSerializer, CommentListSerializer, StorySerializer, \
    StoryLikeSerializer, PostListSerializer, StoryListSerializer
from post.utils.handle_private import generate_like_queryset, generate_comment_queryset
from post.utils.serialize_comments import build_comment_tree
from user.models import PrivacyChoice


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
            return (Post.objects.prefetch_related('hashtags').select_related('author').filter(hashtags__name__iexact=hashtag)
                    .filter(is_deleted=False).filter(author__privacy_choice="public"))
        return (Post.objects.prefetch_related('hashtags').select_related('author').filter(is_deleted=False)
                .filter(author__privacy_choice="public"))

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_serializer_class(self):
        if self.action == 'list':
            return PostListSerializer
        return PostSerializer


class StoryViewSet(ModelViewSet):
    """
    ViewSet for managing stories.
    This ViewSet provides CRUD operations for the Story model.
    It allows users to create, retrieve, update, and delete stories.
    Stories can be filtered by hashtags using the 'hashtag' query parameter.
    The queryset only includes stories that are not marked as deleted.
    The serializer used is StorySerializer, which handles the serialization and deserialization of Story instances.
    The ordering is set to display the most recent stories first.
    The get_queryset method filters stories based on the 'hashtag' query parameter if provided.
    """
    queryset = Story.objects.filter(is_deleted=False)
    serializer_class = StorySerializer
    pagination_class = CursorPagination

    ordering = ['-created_at']

    def get_queryset(self):
        hashtag = self.request.query_params.get('hashtag')
        if hashtag:
            return (Story.objects.prefetch_related('hashtags').select_related('author').filter(hashtags__name__iexact=hashtag)
                    .filter(is_deleted=False).filter(is_expired=False).filter(author__privacy_choice="public"))
        return (Story.objects.prefetch_related('hashtags').select_related('author').filter(is_deleted=False)
                .filter(is_expired=False).filter(author__privacy_choice="public"))

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_serializer_class(self):
        if self.action == 'list':
            return StoryListSerializer
        return StorySerializer

    @action(detail=False, methods=['get'], url_path='expired_stories')
    def get_expired(self, request, *args, **kwargs):
        """
        Custom action to retrieve expired stories.
        This action returns all stories that are marked as expired.
        It can be accessed via the URL /stories/expired_stories/.
        """
        user = request.user
        if not user.is_authenticated:
            return Response({"detail": "Authentication credentials were not provided."}, status=401)
        expired_stories = Story.objects.filter(is_expired=True).filter(author=user)
        serializer = self.get_serializer(expired_stories, many=True)
        return Response(serializer.data)


class BaseLikeViewSet(ModelViewSet):
    serializer_class = LikeSerializer
    pagination_class = CursorPagination
    ordering = ['-created_at']

    def get_queryset(self):
        content_type = self.request.query_params.get('type')
        content_id = self.request.query_params.get('id')
        user = self.request.user

        if content_type not in ['post', 'story']:
            raise ValidationError("Missing or invalid 'type' parameter. Must be 'post' or 'story'.")

        return generate_like_queryset(content_type, content_id, user)

    def perform_update(self, serializer):
        raise NotImplementedError

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context

    def get_serializer_class(self):
        content_type = self.request.query_params.get('type')
        if content_type == 'post':
            return LikeSerializer
        else:
            return StoryLikeSerializer


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
    pagination_class = CursorPagination

    ordering = ['-created_at']

    def get_queryset(self):
        post_id = self.request.query_params.get('post_id')
        user = self.request.user

        return generate_comment_queryset(post_id, user)

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
