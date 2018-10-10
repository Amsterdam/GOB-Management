import graphene

from graphene_sqlalchemy import SQLAlchemyObjectType

from api.database.models import Log
from api.fields import FilterConnectionField

# Create a generic class to mutualize description of people attributes for both queries and mutations
class LogAttribute:
    logid = graphene.Int(description="Name of the person.")
    timestamp = graphene.DateTime(description="Height of the person.")
    process_id = graphene.String(description="Mass of the person.")
    source = graphene.String(description="Hair color of the person.")
    entity = graphene.String(description="Skin color of the person.")
    level = graphene.String(description="Eye color of the person.")
    name = graphene.String(description="Birth year of the person.")
    msg = graphene.String(description="Gender of the person.")
    data = graphene.JSONString(description="Global Id of the planet from which the person comes from.")


class LogType(SQLAlchemyObjectType):
    """Log node."""

    class Meta:
        model = Log
        interfaces = (graphene.relay.Node,)


class LogConnection(graphene.relay.Connection):
    class Meta:
        node = LogType


class Query(graphene.ObjectType):
    """Query objects for GraphQL API."""

    node = graphene.relay.Node.Field()
    logs = FilterConnectionField(LogConnection, process_id=graphene.String())

schema = graphene.Schema(query=Query)
