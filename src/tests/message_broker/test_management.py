from unittest import TestCase
from unittest.mock import patch, ANY

from gobmanagement.message_broker.management import _get, get_queues

class TestManagement(TestCase):
    @patch('gobmanagement.message_broker.management.requests')
    def test_get(self, mock_requests):
        _get("any path")
        mock_requests.get.assert_called_with(ANY, auth=ANY)

    @patch('gobmanagement.message_broker.management._get')
    def test_get_queueu(self, mock_get):
        get_queues()
        mock_get.assert_called_with(ANY)


