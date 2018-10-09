import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField

from api.models import Log

# Schema Objects
class LogObject(SQLAlchemyObjectType):
    class Meta:
        model = Log
        interfaces = (graphene.relay.Node, )

class Query(graphene.ObjectType):
    node = graphene.relay.Node.Field()
    logs = SQLAlchemyConnectionField(LogObject)

schema = graphene.Schema(query=Query)
