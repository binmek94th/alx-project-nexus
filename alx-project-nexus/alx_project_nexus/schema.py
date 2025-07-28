import graphene
import post.schema


class Query(post.schema.Query, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query)
