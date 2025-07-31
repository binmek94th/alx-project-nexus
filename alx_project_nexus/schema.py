import graphene
import post.schema
import user.schema


class Query(post.schema.Query, user.schema.Query, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query)
