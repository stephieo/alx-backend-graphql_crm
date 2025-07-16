import graphene
from graphene_django import DjangoObjectType
from crm.schema import Mutation as CRMMutation, Query as CRMQuery

class Query(CRMQuery, graphene.ObjectType):
    pass
#project level mutation
class Mutation(CRMMutation, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)