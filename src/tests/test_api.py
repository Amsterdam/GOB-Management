import collections
import contextlib

from gobmanagement import api


@contextlib.contextmanager
def mock_session(*args, **kwargs):
    yield 10


def test_session_middleware():
    middleware = api.create_session_middleware(
        mock_session
    )
    result = middleware(
        lambda r, i: i.context['session'],
        {}, collections.namedtuple("info", ["context"])
    )
    assert result == 10