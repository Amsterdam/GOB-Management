from unittest import TestCase, mock

from gobmanagement import api

class MockedRequest:

    def __init__(self):
        self.host = "any host"
        self.headers = {}
        self.method = 'POST'


mock_request = MockedRequest()

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
    @mock.patch('gobmanagement.api.purge_queue')
    def test_queue(self, purge_queue):
        mock_request = mock.MagicMock()

        with mock.patch('gobmanagement.api.request', mock_request):
            mock_request.method = 'DELETE'
            purge_queue.return_value = ('any result', 'any status code')
            api._queue('any queue name')
            purge_queue.assert_called_with('any queue name')

            # Only DELETE queue has been implemented
            for method in ['GET', 'POST', 'PUT', 'PATCH', 'ANY OTHER METHOD']:
                mock_request.method = method
                with self.assertRaises(AssertionError):
                    api._queue('any queue name')

class TestState(TestCase):

    @mock.patch('gobmanagement.api.jsonify')
    @mock.patch('gobmanagement.api.get_process_state')
    def test_process_state(self, mock_get_process_state, mock_jsonify):
        result = api._process_state("any process id")
        mock_jsonify.assert_called_with(mock_get_process_state.return_value)
        self.assertEqual(result, mock_jsonify.return_value)

    @mock.patch('gobmanagement.api.jsonify')
    @mock.patch('gobmanagement.api.get_queues')
    def test_workflow_state(self, mock_queues, mock_jsonify):
        from gobcore.message_broker.notifications import NOTIFY_EXCHANGE
        from gobcore.message_broker.config import WORKFLOW_QUEUE

        queues = [
            {
                'name': 'q1',
                'messages_unacknowledged': 0,
                'x': 0
            },
            {
                'name': NOTIFY_EXCHANGE,
                'messages_unacknowledged': 1,
                'x': 1
            },
            {
                'name': f'{NOTIFY_EXCHANGE}.something more',
                'messages_unacknowledged': 2,
                'x': 2
            },
            {
                'name': WORKFLOW_QUEUE,
                'messages_unacknowledged': 3,
                'x': 3
            },
        ]
        mock_queues.return_value = queues, None
        result = api._workflow_state()
        mock_jsonify.assert_called_with([{
            'name': queue['name'],
            'messages_unacknowledged': queue['messages_unacknowledged']
        } for queue in queues[1:]])
        self.assertEqual(result, mock_jsonify.return_value)


class TestSecurityMiddlewareLoaded(TestCase):

    def test_loaded(self):
        self.assertTrue(isinstance(api.security_middleware, api.SecurityMiddleware))
