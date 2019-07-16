import inspect

from unittest import TestCase
from unittest.mock import patch, MagicMock

from gobmanagement.grpc.out import jobs_pb2_grpc, jobs_pb2
from gobmanagement.grpc.services.jobs import JobsServicer, WORKFLOW_EXCHANGE, WORKFLOW_REQUEST_KEY, StartCommand


@patch("gobmanagement.grpc.services.jobs.StartCommands")
class TestJobsServicer(TestCase):

    def test_implemented_methods(self, mock_start_commands):
        """Assert that JobsServicer implements all methods defined in jobs_pb2_grpc.JobsServicer"""

        methods = inspect.getmembers(jobs_pb2_grpc.JobsServicer, predicate=inspect.isroutine)
        methods = [name for name, _ in methods if not name.startswith('__')]

        jobs_servicer = JobsServicer()

        # Should not raise AttributeError
        for method in methods:
            getattr(jobs_servicer, method)

    def test_getattr(self, mock_start_commands):
        jobs_servicer = JobsServicer()
        jobs_servicer.start_job = MagicMock()

        jobs_servicer.StartSomeJob('request', 'context')
        jobs_servicer.start_job.assert_called_with('some', 'request', 'context')

        jobs_servicer.StartSome_UnderscoredJob('request', 'context')
        jobs_servicer.start_job.assert_called_with('some_underscored', 'request', 'context')

        with self.assertRaises(AttributeError):
            jobs_servicer.SomeOtherMethodThatsNotCaught()

    @patch("gobmanagement.grpc.services.jobs.publish")
    def test_start_job(self, mock_publish, mock_start_commands):
        jobs_servicer = JobsServicer()
        jobs_servicer._extract_args = MagicMock(return_value=['arg1', 'arg2'])
        jobs_servicer.startcommands = MagicMock()

        class MockCommand:
            workflow = 'some workflow'
            start_step = 'some start step'

            validate_arguments = MagicMock()

        command = MockCommand()
        jobs_servicer.startcommands.get.return_value = command

        res = jobs_servicer.start_job('name', 'request', 'context')
        jobs_servicer.startcommands.get.assert_called_with('name')
        command.validate_arguments.assert_called_with(['arg1', 'arg2'])

        msg = {
            'workflow': {
                'workflow_name': 'some workflow',
                'step_name': 'some start step',
            },
            'header': jobs_servicer._extract_args.return_value,
        }

        mock_publish.assert_called_with(WORKFLOW_EXCHANGE, WORKFLOW_REQUEST_KEY, msg)
        self.assertIsInstance(res, jobs_pb2.JobResponse)
        self.assertEqual('OK', res.status)

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

        result = jobs_servicer._extract_args(start_command, {'arg1': 'someval1', 'arg2': 'someval2', 'arg3': None})

        self.assertEqual(result, {
            'arg1': 'someval1',
            'arg2': 'someval2',
            # arg3 is ignored, not set in request
        })
