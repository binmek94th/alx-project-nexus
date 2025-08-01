import graphene
import post.schema
import user.schema


class Query(post.schema.Query, user.schema.Query, graphene.ObjectType):
    pass


class Mutation(post.schema.Mutation, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
