from unittest import TestCase
from unittest.mock import patch, MagicMock

from gobmanagement.security import SecurityMiddleware, _PUBLIC, GOB_ADMIN, GOB_ADMIN_R


class TestSecurityMiddleware(TestCase):

    def test_init(self):
        app = MagicMock()
        middleware = SecurityMiddleware(app)
        app.before_request.assert_called_with(middleware._before_request)

    @patch("gobmanagement.security.extract_roles")
    def test_before_request(self, mock_extract_roles):
        mock_request = MagicMock()
        with patch("gobmanagement.security.request", mock_request):

            middleware = SecurityMiddleware(MagicMock())
            middleware._match_path = MagicMock()
            middleware._is_allowed_access = MagicMock(return_value=True)

            # OK case. Access allowed
            self.assertIsNone(middleware._before_request())
            middleware._match_path.assert_called_with(mock_request.path, mock_request.method)
            mock_extract_roles.assert_called_with(mock_request.headers)

            middleware._is_allowed_access.assert_called_with(mock_extract_roles.return_value, middleware._match_path.return_value)

            # Access denied, allowed_access returns False
            middleware._is_allowed_access.return_value = False
            self.assertEqual(("Forbidden", 403), middleware._before_request())

            # Access denied, no route matches
            middleware._is_allowed_access.return_value = True
            middleware._match_path.return_value = None
            self.assertEqual(("Forbidden", 403), middleware._before_request())

    def test_is_allowed_access(self):
        match = {
            'methods': ['NOT', 'IMPORTANT', 'GET', 'POST'],
            'roles': ['roleA', 'roleB'],
        }
        middleware = SecurityMiddleware(MagicMock())
        self.assertFalse(middleware._is_allowed_access([], match))
        self.assertFalse(middleware._is_allowed_access(['roleC'], match))
        self.assertTrue(middleware._is_allowed_access(['roleA'], match))
        self.assertTrue(middleware._is_allowed_access(['roleB'], match))
        self.assertTrue(middleware._is_allowed_access(['roleA', 'roleB'], match))

        match['roles'] = []
        self.assertFalse(middleware._is_allowed_access(['roleA'], match))
        self.assertFalse(middleware._is_allowed_access([], match))

        match['roles'] = _PUBLIC
        self.assertTrue(middleware._is_allowed_access([], match))

    def test_match_path(self):
        middleware = SecurityMiddleware(MagicMock())

        testcases = [
            ('/status/health/', 'GET', _PUBLIC),
            ('/status/health', 'GET', _PUBLIC),
            ('/status/health', 'POST', None),
            ('/gob_management/job', 'POST', [GOB_ADMIN]),
            ('/gob_management/job', 'DELETE', None),
            ('/gob_management/job/1', 'DELETE', [GOB_ADMIN]),
            ('/gob_management/job/1', 'GET', None),
            ('/gob_management/catalogs', 'GET', [GOB_ADMIN, GOB_ADMIN_R]),
            ('/gob_management/catalogs/', 'GET', [GOB_ADMIN, GOB_ADMIN_R]),
            ('/gob_management/queues/', 'GET', [GOB_ADMIN, GOB_ADMIN_R]),
            ('/gob_management/queues/', 'POST', [GOB_ADMIN, GOB_ADMIN_R]),
            ('/gob_management/queue/a', 'POST', None),
            ('/gob_management/queue/a', 'DELETE', [GOB_ADMIN]),
            ('/gob_management/public/state/process/1', 'GET', _PUBLIC),
            ('/gob_management/public/state/process/1', 'POST', None),
            ('/gob_management/public/state/workflow', 'GET', _PUBLIC),
            ('/gob_management/public/state/workflow/', 'GET', _PUBLIC),
            ('/gob_management/public/state/workflow/', 'POST', None),
        ]

        for path, method, expected_result in testcases:
            matched = middleware._match_path(path, method)

            if expected_result is None:
                self.assertIsNone(matched, f"Expected match for path {path} and method {method} to be None.")
            else:
                self.assertIsNotNone(matched, f"Expected to have a match for path {path} and method {method}")
                self.assertEqual(expected_result, matched['roles'], f"Expected path {path} with method {method} to be matched with {','.join(expected_result) if isinstance(expected_result, list) else expected_result}")
