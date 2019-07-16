from unittest import TestCase, mock

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

class MockedRequest:

    def __init__(self):
        self.host = "any host"
        self.headers = {}

mock_request = MockedRequest()

class TestJob(TestCase):

    def setUp(self) -> None:
        mock_request = MockedRequest()

    @mock.patch('gobmanagement.api.request', mock_request)
    def test_job_errors(self):
        msg, status = api._job()
        assert status == 401

        mock_request.headers['X-Auth-Userid'] = "any userid"
        msg, status = api._job()
        assert status == 403

        mock_request.headers['X-Auth-Roles'] = "any role"
        msg, status = api._job()
        assert status == 403

        mock_request.headers['X-Auth-Roles'] = "any role gob_adm"
        mock_request.get_json = lambda silent: {}
        msg, status = api._job()
        assert status == 400
