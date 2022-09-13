from unittest import TestCase
from unittest.mock import patch

from gobmanagement.config import API_PORT

class TestMain(TestCase):

    @patch('gobmanagement.api.app')
    @patch('gobmanagement.api.socketio.run')
    def test_socketio_run(self, mock_socketio_run, mock_app):
        from gobmanagement import __main__
        mock_socketio_run.assert_called_with(app=mock_app, port=API_PORT)
