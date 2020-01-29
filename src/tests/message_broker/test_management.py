from unittest import TestCase
from unittest.mock import patch, ANY

from gobmanagement.message_broker.management import _request, get_queues, purge_queue

class TestManagement(TestCase):
    @patch('gobmanagement.message_broker.management.requests')
    def test_get(self, mock_requests):
        _request("any path")
        mock_requests.get.assert_called_with(ANY, auth=ANY)

    @patch('gobmanagement.message_broker.management._request')
    def test_get_queues(self, mock_request):
        get_queues()
        mock_request.assert_called_with(ANY)

    @patch('gobmanagement.message_broker.management._request')
    def test_purge_queue(self, mock_request):
        purge_queue('any queue')
        mock_request.assert_called_with(ANY, method='delete')
