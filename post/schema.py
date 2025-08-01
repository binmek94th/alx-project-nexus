import base64
import uuid

import django_filters
import graphene
from django.core.files.base import ContentFile
from django.db.models import Q
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphene_file_upload.scalars import Upload
from graphql import GraphQLError

from .models import Post, Like, Comment, Story
from user.models import User, PrivacyChoice


class PostFilterSet(django_filters.FilterSet):
    """
    Filter set for Post model to filter by author and creation date.
    This filter set allows filtering posts based on the author and the date they were created.
    """
    class Meta:
        model = Post
        fields = ['author', 'created_at']


class StoryFilterSet(django_filters.FilterSet):
    """
    Filter set for Story model to filter by author and creation date.
    This filter set allows filtering stories based on the author and the date they were created.
    """
    class Meta:
        model = Story
        fields = ['author', 'created_at']


class UserType(DjangoObjectType):
    """
    GraphQL type for User model.
    This type includes fields such as id, username, profile_picture, bio, and created_at
    """
    class Meta:
        model = User
        interfaces = (relay.Node,)
        fields = ("id", "username", "profile_picture", "full_name", "bio")


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
        fields = ("id", "caption", "author", "created_at")

    def resolve_like_count(self, info):
        return Like.objects.filter(post_id=self.id).count()

    def resolve_comment_count(self, info):
        return Comment.objects.filter(post_id=self.id).count()

    def resolve_author(self, info):
        return self.author


class PostInput(graphene.InputObjectType):
    caption = graphene.String(required=True)


class CreatePost(graphene.Mutation):
    class Arguments:
        input = PostInput(required=True)
        image = Upload(required=True)

    post = graphene.Field(PostType)

    def mutate(self, info, input, image):
        user = info.context.user
        if not user.is_authenticated:
            raise Exception("Authentication required")

        post = Post.objects.create(
            caption=input.caption,
            image=image,
            author=user
        )
        return CreatePost(post=post)


class UpdatePost(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        caption = graphene.String(required=False)
        image = Upload(required=False)  # only if using file upload

    post = graphene.Field(PostType)

    def mutate(self, info, id, caption=None, image=None):
        try:
            post = Post.objects.get(pk=id)
        except Post.DoesNotExist:
            raise GraphQLError("Post not found.")

        if caption:
            post.caption = caption
        if image:
            post.image = image

        post.save()
        return UpdatePost(post=post)


class DeletePost(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    def mutate(self, info, id):
        try:
            post = Post.objects.get(pk=id)
            post.is_deleted = True
            post.save()
            return DeletePost(ok=True)
        except Post.DoesNotExist:
            raise GraphQLError("Post not found.")


class StoryType(DjangoObjectType):
    """
    GraphQL type for Story model.
    This type includes fields such as id, caption, author, created_at, and expires_at
    The author field resolves to the UserType, representing the user who created the story.
    The StoryType allows clients to query for stories, including the author information.
    It also includes a field for the author, which returns the UserType.
    """
    author = graphene.Field(UserType)

    class Meta:
        model = Story
        interfaces = (relay.Node,)
        fields = ("id", "caption", "author", "created_at", "expires_at")

    def resolve_author(self, info):
        return self.author


class Query(graphene.ObjectType):
    """
    GraphQL query for fetching all posts and stories.
    This query allows clients to retrieve all posts amd stories with optional filtering.
    It uses the DjangoFilterConnectionField to enable filtering based on the PostFilterSet or StoryFilterSet.
    The resolve_all_posts method retrieves all posts from the database, selecting related
    author information to optimize database queries.
    The resolve_all_stories method retrieves all stories from the database, also selecting
    related author information.
    """
    all_posts = DjangoFilterConnectionField(PostType, filterset_class=PostFilterSet)
    all_stories = DjangoFilterConnectionField(StoryType, filterset_class=StoryFilterSet)

    def resolve_all_posts(root, info, **kwargs):
        user = info.context.user

        base_filter = Q(author__privacy_choice=PrivacyChoice.PUBLIC)

        if user.is_authenticated:
            base_filter |= Q(author__in=User.objects.filter(followers__follower=user))

        return Post.objects.select_related('author').filter(
            Q(is_deleted=False) & base_filter
        )

    def resolve_all_stories(root, info, **kwargs):
        user = info.context.user

        base_filter = Q(author__privacy_choice=PrivacyChoice.PUBLIC)

        if user.is_authenticated:
            base_filter |= Q(author__in=User.objects.filter(followers__follower=user))

        return Story.objects.select_related('author').filter(
            Q(is_deleted=False) & base_filter
        )


class Mutation(graphene.ObjectType):
    create_post = CreatePost.Field()
    update_post = UpdatePost.Field()
    delete_post = DeletePost.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
