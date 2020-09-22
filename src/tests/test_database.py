from sqlalchemy.sql.elements import TextClause

from unittest import TestCase, mock
from unittest.mock import MagicMock

from gobmanagement.database import remove_job, unfinished_jobs, get_process_state

class TestDatabase(TestCase):

    @mock.patch('gobmanagement.database.session_scope')
    def test_unfinished_jobs(self, mock_scope):
        result = unfinished_jobs()
        self.assertEqual(result, [])

        mock_session = MagicMock()
        mock_scope.return_value.__enter__.return_value = mock_session
        result = unfinished_jobs()
        self.assertEqual(result, [])
        mock_session.execute.assert_called_with("SELECT * FROM jobs where status != 'ended'")

    @mock.patch('gobmanagement.database.unfinished_jobs')
    @mock.patch('gobmanagement.database.session_scope')
    def test_remove_job(self, mock_scope, mock_jobs):
        mock_jobs.return_value = "jobs"
        result = remove_job('any id')
        self.assertEqual(result, "jobs")

        mock_session = MagicMock()
        mock_scope.return_value.__enter__.return_value = mock_session
        remove_job('any id')
        mock_session.execute.assert_called_once()

    @mock.patch('gobmanagement.database.session_scope')
    def test_process_state(self, mock_scope):
        mock_session = MagicMock()
        mock_scope.return_value.__enter__.return_value = mock_session

        result = get_process_state("any process id")
        self.assertEqual(result, [])
        mock_session.execute.assert_called_once()
        args, _ = mock_session.execute.call_args_list[0]
        self.assertEqual(len(args), 1)
        self.assertTrue(isinstance(args[0], TextClause))
