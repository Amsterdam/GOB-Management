from sqlalchemy import func

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
