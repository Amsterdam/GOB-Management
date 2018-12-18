from sqlalchemy import func

from gobcore.model.sa.management import Log

from gobmanagement.database.base import db_session


def get_last_logid():
    """Get logid of last Log message

    :return: value of last logid or None
    """
    return db_session.query(func.max(Log.logid)).scalar()
