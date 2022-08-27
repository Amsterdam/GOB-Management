from unittest import TestCase, mock


class TestWsgi(TestCase):

    @mock.patch('gobmanagement.api.app')
    def test_wsgi(self, mock_app):
        from gobmanagement.wsgi import application
        self.assertEqual(application, mock_app)
