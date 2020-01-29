from sqlalchemy import func

from gobmanagement.database.base import session_scope

from gobcore.model.sa.management import Log, Service


def get_last_logid(session):
    """Get logid of last Log message

    :return: value of last logid or None
    """
    return session.query(func.max(Log.logid)).scalar()


def get_last_service_timestamp(session):
    """Get timestamp of most recent service

    :return: value of most recent timestamp or None
    """
    return session.query(func.max(Service.timestamp)).scalar()


def unfinished_jobs():
    """
    Returns a list of unfinished jobs

    :return:
    """
    stmt = "SELECT * FROM jobs where status != 'ended'"
    with session_scope(True) as session:
        result = session.execute(stmt)
    jobs = [dict(row) for row in result]
    result.close()
    return jobs


def remove_job(job_id):
    """
    Removes the job with the specified id.

    Jobs might be removed when for instance the status is rejected
    :param job_id:
    :return:
    """
    stmt = f"""
DELETE FROM tasks    WHERE jobid={job_id};
DELETE FROM logs     WHERE jobid={job_id};
DELETE FROM jobsteps WHERE jobid={job_id};
DELETE FROM jobs     WHERE    id={job_id};
COMMIT;
"""
    with session_scope(True) as session:
        result = session.execute(stmt)
    result.close()
    return unfinished_jobs()
