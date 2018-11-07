from sqlalchemy import Column, DateTime, Integer, JSON, String

from .base import Base


class Log(Base):
    __tablename__ = 'logs'

    logid = Column(Integer, primary_key=True)
    timestamp = Column(DateTime)
    process_id = Column(String)
    source = Column(String)
    destination = Column(String)
    catalogue = Column(String)
    entity = Column(String)
    level = Column(String)
    name = Column(String)
    msgid = Column("id", String)
    msg = Column(String)
    data = Column(JSON)

    def __repr__(self):
        return f'<Msg {self.msg}>'
