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
    job_id = graphene.Int(description="Id of the job")
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
    step = graphene.String(description="Last step")
    status = graphene.String(description="Status of last step")

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
        filter = " AND ".join([f"{key} = '{value}'" for key, value in kwargs.items()]) if kwargs else ""

        query = """
SELECT log.process_id                AS process_id,
       job.id                        AS job_id,
       date(job.start)               AS day,
       log.name                      AS name,
       log.source                    AS source,
       log.applicatiON               AS application,
       log.destinatiON               AS destination,
       log.catalogue                 AS catalogue,
       log.entity                    AS entity,
       job.start                     AS starttime,
       date_part('year', job.start)  AS startyear,
       date_part('month', job.start) AS startmonth,
       job.end                       AS endtime,
       date_part('year', job.end)    AS endyear,
       date_part('month', job.end)   AS endmonth,
       msg.infos                     AS infos,
       msg.warnings                  AS warnings,
       msg.errors                    AS errors,
       step.name                     AS step,
       step.status                   AS status
FROM jobs AS job
JOIN (
    SELECT jobid      AS jobid,
           min(logid) AS logid
    FROM   logs
    GROUP BY jobid
) AS firstlog ON firstlog.jobid = job.id
JOIN (
    SELECT logid,
           name,
           process_id,
           application,
           source,
           destination,
           catalogue,
           entity
    FROM   logs
) AS log ON log.logid = firstlog.logid
JOIN (
    SELECT jobid   AS jobid,
           max(id) AS stepid
    FROM   jobsteps
    GROUP BY jobid
) AS laststep ON laststep.jobid = job.id
JOIN (
    SELECT id,
           name,
           status
    FROM   jobsteps
) AS step ON step.id = laststep.stepid
LEFT OUTER JOIN (
    SELECT msg.jobid AS jobid,
           inf.count AS infos,
           wrn.count AS warnings,
           err.count AS errors
    FROM (
             SELECT jobid,
                    level,
                    count(*)
             FROM logs
             GROUP BY jobid, level
         ) AS msg
             left outer JOIN logs inf ON msg.jobid = inf.jobid AND msg.level = inf.level AND inf.level = 'INFO'
             left outer JOIN logs wrn ON msg.jobid = wrn.jobid AND msg.level = wrn.level AND wrn.level = 'WARNING'
             left outer JOIN logs err ON msg.jobid = err.jobid AND msg.level = err.level AND err.level = 'ERROR'
    GROUP BY msg.jobid
) AS msg ON msg.jobid = job.id
"""

        statement = f"""
SELECT *
FROM   ( {query} )
AS     result
WHERE  {filter}
ORDER BY starttime DESC
"""
        return [Job(**dict(result)) for result in engine.execute(statement)]


schema = graphene.Schema(query=Query)
