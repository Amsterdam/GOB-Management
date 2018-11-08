import graphene

from graphene_sqlalchemy import SQLAlchemyObjectType

from gobmanagement.database.models import Log
from gobmanagement.database.base import db_session, engine
from gobmanagement.fields import FilterConnectionField


# Create a generic class to mutualize description of people attributes for both queries and mutations
class LogAttribute:
    logid = graphene.Int(description="Unique identification of the log entry")
    timestamp = graphene.DateTime(description="Local timestamp of when the log entry was created")
    process_id = graphene.String(description="The id of the process to which this log entry belongs")
    source = graphene.String(description="The source for the process")
    destination = graphene.String(description="The destination for the process")
    catalogue = graphene.String(description="The catalogue that is handled by the process")
    entity = graphene.String(description="The entity that is handled by the process")
    level = graphene.String(description="The log level (CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET)")
    name = graphene.String(description="The name of the process step that generated the log entry")
    msgid = graphene.String(description="The message id for errors and warnings (allows grouping)")
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


class MsgCategory(graphene.ObjectType):
    level = graphene.String()
    count = graphene.Int()

    def __init__(self, level, count):
        self.level = level
        self.count = count


class LogDay(graphene.ObjectType):

    date = graphene.DateTime(description="Date of the log")
    job = graphene.String(description="Job id of the log")
    level = graphene.String(description="Log level (eg INFO, WARNING, ...)")
    count = graphene.Int(description="Number of messages at the given date and for the given level")

    def __init__(self, date, job, level, count):
        self.date = date
        self.job = job
        self.level = level
        self.count = count

    class Meta:
        interfaces = (graphene.relay.Node,)


class SourceEntity(graphene.ObjectType):

    source = graphene.String(description="The source for the process")
    catalogue = graphene.String(description="The catalogue of the entity that is handled by the process")
    entity = graphene.String(description="The entity that is handled by the process")

    def __init__(self, source, catalogue, entity):
        self.source = source
        self.catalogue = catalogue
        self.entity = entity

    class Meta:
        interfaces = (graphene.relay.Node,)


class Query(graphene.ObjectType):
    """Query objects for GraphQL API."""
    node = graphene.relay.Node.Field()
    logs = FilterConnectionField(LogConnection,
                                 process_id=graphene.String(),
                                 source=graphene.String(),
                                 catalogue=graphene.String(),
                                 entity=graphene.String())

    source_entities = graphene.List(SourceEntity)
    log_days = graphene.List(LogDay,
                             source=graphene.String(),
                             catalogue=graphene.String(),
                             entity=graphene.String())

    def resolve_source_entities(self, _):
        results = db_session.query(Log).distinct(Log.source, Log.catalogue, Log.entity).all()
        return [SourceEntity(result.source, result.catalogue, result.entity) for result in results]

    def resolve_log_days(self, _, **kwargs):
        filter = "WHERE " + " AND ".join([f"{key} = '{value}'" for key, value in kwargs.items()]) if kwargs else ""
        statement = f"""
            SELECT DATE(timestamp) AS logdate,
                   process_id as job,
                   level,
                   COUNT(*) AS count
            FROM logs
            {filter}
            GROUP BY logdate, job, level
            ORDER BY logdate        
        """
        return [LogDay(result.logdate, result.job, result.level, result.count) for result in engine.execute(statement)]


schema = graphene.Schema(query=Query)
