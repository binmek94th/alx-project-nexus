import graphene
from graphene import relay
from graphene_django import DjangoObjectType
from graphql_relay import from_global_id

from post.schema import UserType, PostType
from post.models import Post
from user.models import User


class UserDetailType(DjangoObjectType):
    user = graphene.Field(UserType)
    followers_count = graphene.Int()
    following_count = graphene.Int()
    posts = graphene.List(PostType)

    class Meta:
        model = User
        interfaces = (relay.Node,)
        fields = ("id", "username", "profile_picture", "full_name", "bio")

    def resolve_followers_count(self, info):
        return self.followers.count()

    def resolve_following_count(self, info):
        return self.following.count()

    def resolve_posts(self, info):
        return Post.objects.filter(author=self, is_deleted=False)


class Query(graphene.ObjectType):
    user = graphene.Field(UserDetailType, id=graphene.ID(required=True))

    def resolve_user(self, info, id):
        type_name, user_id = from_global_id(id)
        return User.objects.get(id=user_id)


schema = graphene.Schema(query=Query)
