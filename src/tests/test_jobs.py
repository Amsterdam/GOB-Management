from unittest import TestCase
from unittest.mock import patch

from gobmanagement.jobs import JobsServicer, StartCommand


@patch("gobmanagement.jobs.StartCommands")
class TestJobsServicer(TestCase):

    def test_extract_args(self, mock_start_commands):
        start_command = StartCommand('command', {
            'workflow': 'some workflow',
            'args': [{
                'name': 'arg1',
            }, {
                'name': 'arg2',
            }, {
                'name': 'arg3',
            }]
        })

        class MockRequest:
            arg1 = 'someval1'
            arg2 = 'someval2'
            arg3 = None

        jobs_servicer = JobsServicer()
        result = jobs_servicer._extract_args(start_command, MockRequest())

        self.assertEqual(result, {
            'arg1': 'someval1',
            'arg2': 'someval2',
            # arg3 is ignored, not set in request
        })

        result = jobs_servicer._extract_args(
                start_command, {'arg1': 'someval1', 'arg2': 'someval2', 'arg3': None})

        self.assertEqual(result, {
            'arg1': 'someval1',
            'arg2': 'someval2',
            # arg3 is ignored, not set in request
        })
