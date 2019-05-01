"""Custom scalars
"""
from graphene.types import Scalar


class Timedelta(Scalar):

    @staticmethod
    def serialize(dt):
        """
        Serializes a datetime.timedelta

        str(dt) return "hh:mm:ss.msecs"

        :param dt: datetime.timedelta value
        :return:
        """
        return str(dt).split('.')[0]  # Remove any milliseconds
