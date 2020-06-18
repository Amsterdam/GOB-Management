from unittest import TestCase, mock

from gobmanagement import api

class MockedRequest:

    def __init__(self):
        self.host = "any host"
        self.headers = {}
        self.method = 'POST'

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

class MockModel:

    def get_catalogs(self):
        return {
            'catalog1': {
                'collections': {
                    'coll1': {},
                    'coll2': {}
                }
            }
        }

class TestCatalogs(TestCase):

    def setUp(self) -> None:
        pass

    @mock.patch('gobmanagement.api.GOBModel', MockModel)
    @mock.patch('gobmanagement.api.jsonify', lambda x : x)
    def test_catalogs(self):
        result = api._catalogs();
        self.assertEqual(result, ({'catalog1': ['coll1', 'coll2']}, 200, {'Content-Type': 'application/json'}))

class TestQueues(TestCase):

    @mock.patch('gobmanagement.api.jsonify', lambda x : x)
    @mock.patch('gobmanagement.api.get_queues')
    def test_queues(self, mock_get_queues):
        mock_get_queues.return_value = ('any result', 'any status code')
        api._queues();
        mock_get_queues.assert_called()

    @mock.patch('gobmanagement.api.jsonify', lambda x : x)
    @mock.patch('gobmanagement.api.request')
    @mock.patch('gobmanagement.api.purge_queue')
    def test_queue(self, purge_queue, mock_request):
        mock_request.method = 'DELETE'
        purge_queue.return_value = ('any result', 'any status code')
        api._queue('any queue name')
        purge_queue.assert_called_with('any queue name')

        # Only DELETE queue has been implemented
        for method in ['GET', 'POST', 'PUT', 'PATCH', 'ANY OTHER METHOD']:
            mock_request.method = method
            with self.assertRaises(AssertionError):
                api._queue('any queue name')
