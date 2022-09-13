from unittest import TestCase
from unittest.mock import patch, MagicMock

from gobmanagement.jobs import JobHandler, WORKFLOW_EXCHANGE, WORKFLOW_REQUEST_KEY, StartCommand


@patch("gobmanagement.jobs.StartCommands")
class TestJobHandler(TestCase):

    @patch("gobmanagement.jobs.publish")
    def test_publish_job(self, mock_publish, mock_start_commands):
        job_handler = JobHandler()
        job_handler._extract_args = MagicMock(return_value=['arg1', 'arg2'])
        job_handler.startcommands = mock_start_commands

        class MockCommand:
            workflow = 'some workflow'
            start_step = 'some start step'

            validate_arguments = MagicMock()

        command = MockCommand()
        job_handler.startcommands.get.return_value = command

        res = job_handler.publish_job('name', 'request')
        job_handler.startcommands.get.assert_called_with('name')
        command.validate_arguments.assert_called_with(['arg1', 'arg2'])

        msg = {
            'workflow': {
                'workflow_name': 'some workflow',
                'step_name': 'some start step',
            },
            'header': job_handler._extract_args.return_value,
        }

        mock_publish.assert_called_with(WORKFLOW_EXCHANGE, WORKFLOW_REQUEST_KEY, msg)
        self.assertEqual(res, msg)

    @patch("gobmanagement.jobs.remove_job")
    def test_remove_job(self, mock_remove_job, mock_start_commands):
        job_handler = JobHandler()
        job_id = 12345678
        job_handler.remove_job(job_id)
        mock_remove_job.assert_called_with(job_id)

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

        job_handler = JobHandler()
        result = job_handler._extract_args(start_command, MockRequest())

        self.assertEqual(result, {
            'arg1': 'someval1',
            'arg2': 'someval2',
            # arg3 is ignored, not set in request
        })

        result = job_handler._extract_args(
                start_command, {'arg1': 'someval1', 'arg2': 'someval2', 'arg3': None})

        self.assertEqual(result, {
            'arg1': 'someval1',
            'arg2': 'someval2',
            # arg3 is ignored, not set in request
        })
