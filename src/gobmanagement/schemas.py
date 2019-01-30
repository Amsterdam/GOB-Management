import graphene

from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField

from gobcore.model.sa.management import Log, Service as ServiceModel, ServiceTask as ServiceTaskModel
from gobmanagement.database.base import db_session, engine
from gobmanagement.fields import FilterConnectionField


class Service(SQLAlchemyObjectType):
    service_id = graphene.Int(description="Unique identification of the service")

    class Meta:
        model = ServiceModel
        interfaces = (graphene.relay.Node, )

    def resolve_service_id(self, args):
        return self.id


class ServiceConnection(graphene.relay.Connection):
    class Meta:
        node = Service


class ServiceTask(SQLAlchemyObjectType):
    class Meta:
        model = ServiceTaskModel
        interfaces = (graphene.relay.Node, )


class ServiceTaskConnection(graphene.relay.Connection):
    class Meta:
        node = ServiceTask


# Create a generic class to mutualize description of people attributes for both queries and mutations
class LogAttribute:
    logid = graphene.Int(description="Unique identification of the log entry")
    timestamp = graphene.DateTime(description="Local timestamp of when the log entry was created")
    process_id = graphene.String(description="The id of the process to which this log entry belongs")
    source = graphene.String(description="The source for the process")
    application = graphene.String(description="The application for the process")
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


class Job(graphene.ObjectType):

    process_id = graphene.String(description="Process id of the job")
    day = graphene.String(description="Day that the job has started")
    name = graphene.String(description="Name of the job")
    source = graphene.String(description="Source for the job")
    application = graphene.String(description="Source application for the job")
    destination = graphene.String(description="Destination for the job")
    catalogue = graphene.String(description="Catalogue that is handled by the job")
    entity = graphene.String(description="Entity that is handled by the job")
    starttime = graphene.DateTime(description="Time when the job was started")
    endtime = graphene.String(description="Time when the job has ended")
    infos = graphene.Int(description="Info logs within a job")
    warnings = graphene.Int(description="Warning logs within a job")
    errors = graphene.Int(description="Error logs within a job")

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

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

    services = SQLAlchemyConnectionField(ServiceConnection)

    tasks = SQLAlchemyConnectionField(ServiceTaskConnection)

    jobs = graphene.List(Job,
                         source=graphene.String(),
                         catalogue=graphene.String(),
                         entity=graphene.String(),
                         startyear=graphene.String(),
                         startmonth=graphene.String())

    def resolve_source_entities(self, _):
        results = db_session.query(Log).distinct(Log.source, Log.catalogue, Log.entity).all()
        return [SourceEntity(result.source, result.catalogue, result.entity) for result in results]

    def resolve_jobs(self, _, **kwargs):
        filter = "WHERE " + " AND ".join([f"{key} = '{value}'" for key, value in kwargs.items()]) if kwargs else ""
        statement = f"""
           select * from (
            select job.process_id,
                   firstlog.day,
                   firstlog.name,
                   firstlog.source,
                   firstlog.application,
                   firstlog.destination,
                   firstlog.catalogue,
                   firstlog.entity,
                   firstlog.starttime,
                   firstlog.year as startyear,
                   firstlog.month as startmonth,
                   lastlog.endtime,
                   lastlog.year as endyear,
                   lastlog.month as endmonth,
                   coalesce(infos.count, 0) as infos,
                   coalesce(warnings.count, 0) as warnings,
                   coalesce(errors.count, 0) as errors
            from (
                select process_id,
                       min(logid) as minlogid,
                       max(logid) as maxlogid
                from logs
                group by process_id
            ) as job
            join (
                select logid,
                       name,
                       application,
                       source,
                       destination,
                       catalogue,
                       entity,
                       timestamp as starttime,
                       date(timestamp) as day,
                       date_part('year', timestamp) as year,
                       date_part('month', timestamp) as month
                from logs
            ) as firstlog on firstlog.logid = job.minlogid
            join (
                select logid,
                       timestamp as endtime,
                       date_part('year', timestamp) as year,
                       date_part('month', timestamp) as month
                from logs
            ) as lastlog on lastlog.logid = job.maxlogid
            left outer join (
                select process_id,
                       count(*) as count
                from logs
                where level = 'ERROR'
                group by process_id
            ) as errors on errors.process_id = job.process_id
            left outer join (
                select process_id,
                       count(*) as count
                from logs
                where level = 'WARNING'
                group by process_id
            ) as warnings on warnings.process_id = job.process_id
            left outer join (
                select process_id,
                       count(*) as count
                from logs
                where level = 'INFO'
                group by process_id
            ) as infos on infos.process_id = job.process_id
            order by firstlog.starttime desc
            ) as result
            {filter}
        """
        return [Job(**dict(result)) for result in engine.execute(statement)]


schema = graphene.Schema(query=Query)
