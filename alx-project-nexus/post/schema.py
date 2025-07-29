import django_filters
import graphene
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from .models import Post, Like, Comment
from user.models import User


class PostFilterSet(django_filters.FilterSet):
    """
    Filter set for Post model to filter by author and creation date.
    This filter set allows filtering posts based on the author and the date they were created.
    """
    class Meta:
        model = Post
        fields = ['author', 'created_at']


class UserType(DjangoObjectType):
    """
    GraphQL type for User model.
    This type includes fields such as id, username, profile_picture, bio, and created_at
    """
    class Meta:
        model = User
        interfaces = (relay.Node,)
        fields = ("id", "username", "profile_picture", "bio")


class PostType(DjangoObjectType):
    """
    GraphQL type for Post model.
    This type includes fields such as id, title, caption, image, like_count, comment
    count, and author.
    The like_count and comment_count fields are resolved dynamically to count the
    number of likes and comments associated with the post.
    The author field resolves to the UserType, representing the user who created the post.
    """
    like_count = graphene.Int()
    comment_count = graphene.Int()
    author = graphene.Field(UserType)

    class Meta:
        model = Post
        interfaces = (relay.Node,)
        fields = ("id", "caption", "image", "author", "created_at")

    def resolve_like_count(self, info):
        return Like.objects.filter(post_id=self.id).count()

    def resolve_comment_count(self, info):
        return Comment.objects.filter(post_id=self.id).count()

    def resolve_author(self, info):
        return self.author


class Query(graphene.ObjectType):
    """
    GraphQL query for fetching all posts.
    This query allows clients to retrieve all posts with optional filtering.
    It uses the DjangoFilterConnectionField to enable filtering based on the PostFilterSet.
    The resolve_all_posts method retrieves all posts from the database, selecting related
    author information to optimize database queries.
    """
    all_posts = DjangoFilterConnectionField(PostType, filterset_class=PostFilterSet)

    def resolve_all_posts(root, info, **kwargs):
        return (Post.objects.select_related("author").
                filter(author__privacy_choice=User.PrivacyChoice.PUBLIC, is_deleted=False))


schema = graphene.Schema(query=Query)
