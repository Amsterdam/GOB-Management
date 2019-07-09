from gobmanagement.grpc.out import jobs_pb2

from gobcore.workflow.start_commands import StartCommands, StartCommand
from gobcore.message_broker import publish
from gobcore.message_broker.config import WORKFLOW_EXCHANGE, WORKFLOW_REQUEST_KEY

import re


class JobsServicer:
    """JobsServicer does not extend the JobsServicer from grpc.out.gobmanagement_pb2_grpc. We catch all generated
    methods of the form Start{jobname}Job in this class. Subclassing the generated JobsServicer would mean that our
    __getattr__ method would not be called. A test is written in the test directory that validates that all methods
    defined by the generated JobsServices are handles by this class.

    """
    startcommands = StartCommands()

    def __getattr__(self, name):
        match = re.fullmatch(r'Start(\w*)Job', name)

        if match:
            job_type = match.group(1).lower()
        else:
            raise AttributeError()

        def method(*args):
            return self.start_job(job_type, *args)

        return method

    def start_job(self, name, request, context):
        command = self.startcommands.get(name)
        args = self._extract_args(command, request)
        command.validate_arguments(args)

        msg = {
            'workflow': {
                'workflow_name': command.workflow,
            },
            'header': args
        }

        if command.start_step:
            msg['workflow']['step_name'] = command.start_step

        publish(WORKFLOW_EXCHANGE, WORKFLOW_REQUEST_KEY, msg)

        return jobs_pb2.JobResponse(status='OK')

    def _extract_args(self, command: StartCommand, request):
        args = {}
        for arg in command.args:
            if getattr(request, arg.name):
                args[arg.name] = getattr(request, arg.name)
        return args
