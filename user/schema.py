import django_filters
import graphene
from django.db.models import Count, F, IntegerField, ExpressionWrapper
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql_relay import from_global_id

from post.schema import UserType, PostType
from post.models import Post
from user.models import User


class UserDetailType(DjangoObjectType):
    user = graphene.Field(UserType)
    followers_count = graphene.Int()
    following_count = graphene.Int()
    post_count = graphene.Int()
    posts = graphene.List(PostType)

    class Meta:
        model = User
        interfaces = (relay.Node,)
        fields = ("id", "username", "profile_picture", "full_name", "bio")

    def resolve_followers_count(self, info):
        return self.followers.count()

    def resolve_following_count(self, info):
        return self.following.count()

    def resolve_post_count(self, info):
        return self.posts.count()

    def resolve_posts(self, info):
        return Post.objects.filter(author=self, is_deleted=False)


class Follow(DjangoObjectType):
    user = graphene.Field(UserType)

    class Meta:
        model = User
        interfaces = (relay.Node,)
        fields = ("id", "username", "profile_picture", "full_name", "bio")


class UserNode(DjangoObjectType):
    class Meta:
        model = User
        interfaces = (relay.Node,)
        fields = ("id", "username", "profile_picture", "full_name", "bio")


class UserFilter(django_filters.FilterSet):
    class Meta:
        model = User
        fields = []
        

class Query(graphene.ObjectType):
    user = graphene.Field(UserDetailType, id=graphene.ID(required=True))
    top_users = DjangoFilterConnectionField(UserType, filterset_class=UserFilter)

    def resolve_user(self, info, id):
        type_name, user_id = from_global_id(id)
        return User.objects.get(id=user_id)

    def resolve_top_followers(self, info, **kwargs):
        """
        The rank score is calculated based on the number of followers, following, and post interactions (likes and comments).
        The rank score formula is:
        rank_score = (followers_count * 3) + (post_interaction_score * 2) - following_count
        where post_interaction_score is the sum of like_count and comment_count.
        The method returns a list of User objects annotated with their followers count, following count,
        like count, comment count, post interaction score, and rank score.
        :param info:
        :return:
        """
        return User.objects.annotate(
            followers_count=Count('followers', distinct=True),
            following_count=Count('following', distinct=True),
            like_count=Count('posts__likes', distinct=True),
            comment_count=Count('posts__comments', distinct=True),
        ).annotate(
            post_interaction_score=F('like_count') + F('comment_count'),
            rank_score=ExpressionWrapper(
                F('followers_count') * 3 + F('post_interaction_score') * 2 - F('following_count'),
                output_field=IntegerField()
            )
        ).order_by('-rank_score')


schema = graphene.Schema(query=Query)
