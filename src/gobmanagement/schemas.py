import graphene

from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField

from gobcore.status.heartbeat import STATUS_START, STATUS_SCHEDULED, STATUS_END

from gobcore.model.sa.management import Log, Service as ServiceModel, ServiceTask as ServiceTaskModel

from gobmanagement.database import get_last_logid
from gobmanagement.database.base import session_scope
from gobmanagement.database.base import db_session, engine

from gobmanagement.fields import FilterConnectionField
from gobmanagement.scalars import Timedelta
from gobmanagement.cache import ResolveCache


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
    jobid = graphene.Int(description="Id of the job")
    bruto_duration = Timedelta(description="Bruto duration of the job")
    netto_duration = Timedelta(description="Netto duration of the job")
    age_category = graphene.String(description="Time since job was started as age category")
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


class StepInfo(graphene.ObjectType):
    stepid = graphene.Int()
    name = graphene.String()
    start = graphene.DateTime()
    end = graphene.DateTime()
    duration = Timedelta()
    status = graphene.String()

    def __init__(self, step):
        self.__dict__.update(step)

    class Meta:
        interfaces = (graphene.relay.Node,)


class JobInfo(graphene.ObjectType):
    jobid = graphene.Int()
    name = graphene.String()
    type = graphene.String()
    args = graphene.String()
    start = graphene.DateTime()
    end = graphene.DateTime()
    duration = Timedelta()
    status = graphene.String()

    steps = graphene.List(StepInfo)

    def __init__(self, job, steps):
        self.steps = [StepInfo(step) for step in steps]
        self.__dict__.update(job)

    class Meta:
        interfaces = (graphene.relay.Node,)


class Query(graphene.ObjectType):
    """Query objects for GraphQL API."""
    node = graphene.relay.Node.Field()
    logs = FilterConnectionField(LogConnection,
                                 process_id=graphene.String(),
                                 jobid=graphene.Int(),
                                 stepid=graphene.Int(),
                                 source=graphene.String(),
                                 catalogue=graphene.String(),
                                 entity=graphene.String())

    source_entities = graphene.List(SourceEntity)

    services = SQLAlchemyConnectionField(ServiceConnection)

    tasks = SQLAlchemyConnectionField(ServiceTaskConnection)

    jobs = graphene.List(Job,
                         days_ago=graphene.Int(),
                         jobid=graphene.Int(),
                         source=graphene.String(),
                         catalogue=graphene.String(),
                         entity=graphene.String(),
                         startyear=graphene.String(),
                         startmonth=graphene.String())

    jobinfo = graphene.List(JobInfo, jobid=graphene.Int())

    _resolve_cache = ResolveCache()

    def resolve_jobinfo(self, _, jobid):
        statement = f"""
        SELECT *, id AS jobid, jobs.end - jobs.start AS duration
        FROM jobs
        WHERE id = {jobid}
"""
        jobs = [dict(job) for job in engine.execute(statement)]
        if not jobs:
            return
        job = jobs[0]

        statement = f"""
        SELECT *, id AS stepid, jobsteps.end - jobsteps.start AS duration
        FROM jobsteps
        WHERE jobid = {jobid}
        ORDER BY start
"""
        steps = [dict(step) for step in engine.execute(statement)]

        return [JobInfo(job, steps)]

    def resolve_source_entities(self, _):
        results = db_session.query(Log).distinct(Log.source, Log.catalogue, Log.entity).all()
        return [SourceEntity(result.source, result.catalogue, result.entity) for result in results]

    def resolve_jobs(self, _, **kwargs):
        days_ago = 10
        if "days_ago" in kwargs:
            days_ago = int(kwargs["days_ago"])
            del kwargs["days_ago"]

        where = " AND ".join([f"{key} = '{value}'" for key, value in kwargs.items()]) if kwargs else "True"

        query = f"""
SELECT log.process_id                AS process_id,
       job.id                        AS jobid,
       jobinfo.duration              AS bruto_duration,
       stepdurations.duration        AS netto_duration,
       CASE WHEN jobinfo.time_ago <= '24 hours'::interval THEN ' 0 - 24 uur'
            WHEN jobinfo.time_ago <= '48 hours'::interval THEN '24 - 48 uur'
            WHEN jobinfo.time_ago <= '96 hours'::interval THEN '48 - 96 uur'
                                                          ELSE 'Ouder'
       END                           AS age_category,
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
       case when step.start is null and step.end is null then '{STATUS_SCHEDULED}'
            when step.start is not null and step.end is null then '{STATUS_START}'
            else '{STATUS_END}' end AS status
FROM jobs AS job
JOIN (
    SELECT id,
           jobs.end - jobs.start AS duration,
           now() - jobs.start    AS time_ago
    FROM jobs
) as jobinfo ON jobinfo.id = job.id
JOIN (
    SELECT jobid,
           SUM(jobsteps.end - jobsteps.start) AS duration
    FROM jobsteps
    GROUP BY jobid
) as stepdurations ON stepdurations.jobid = job.id
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
JOIN jobsteps step on step.id = laststep.stepid
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
WHERE jobinfo.time_ago <= '{days_ago} days'::interval
"""

        statement = f"""
SELECT *
FROM   ( {query} )
AS     result
WHERE  {where}
ORDER BY starttime DESC
"""

        # Response will change when a new log has become available
        with session_scope(True) as session:
            last_logid = get_last_logid(session)

        # Response will also change when the statement changes
        return Query._resolve_cache.resolve("resolve_jobs",
                                            last_logid,
                                            statement,
                                            lambda: [Job(**dict(result)) for result in engine.execute(statement)])


schema = graphene.Schema(query=Query)
