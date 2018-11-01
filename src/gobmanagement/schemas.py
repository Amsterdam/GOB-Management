import graphene

from graphene_sqlalchemy import SQLAlchemyObjectType

from gobmanagement.database.models import Log
from gobmanagement.database.base import db_session
from gobmanagement.fields import FilterConnectionField


# Create a generic class to mutualize description of people attributes for both queries and mutations
class LogAttribute:
    logid = graphene.Int(description="Unique identification of the log entry")
    timestamp = graphene.DateTime(description="Local timestamp of when the log entry was created")
    process_id = graphene.String(description="The id of the process to which this log entry belongs")
    source = graphene.String(description="The source for the process")
    entity = graphene.String(description="The entity that is handled by the process")
    level = graphene.String(description="The log level (CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET)")
    name = graphene.String(description="The name of the process step that generated the log entry")
    msg = graphene.String(description="A (short) description of the log entry")
    data = graphene.JSONString(description="Associated data in JSON format for the log entry")


class LogType(SQLAlchemyObjectType, LogAttribute):
    """Log node."""

    class Meta:
        model = Log
        interfaces = (graphene.relay.Node,)


class LogConnection(graphene.relay.Connection):
    class Meta:
        node = LogType


class SourceEntity(graphene.ObjectType):

    source = graphene.String(description="The source for the process")
    entity = graphene.String(description="The entity that is handled by the process")

    def __init__(self, source, entity):
        self.source = source
        self.entity = entity

    class Meta:
        interfaces = (graphene.relay.Node,)


class Query(graphene.ObjectType):
    """Query objects for GraphQL API."""
    node = graphene.relay.Node.Field()
    logs = FilterConnectionField(LogConnection,
                                 process_id=graphene.String(),
                                 source=graphene.String(),
                                 entity=graphene.String())
    source_entities = graphene.List(SourceEntity)

    def resolve_source_entities(self, _):
        results = db_session.query(Log).distinct(Log.source, Log.entity).all()
        return [SourceEntity(result.source, result.entity) for result in results]


schema = graphene.Schema(query=Query)
