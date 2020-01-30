from gobmanagement.grpc.out import jobs_pb2
from gobmanagement.database import remove_job

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

    def publish_job(self, name, request):
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
        return msg

    def start_job(self, name, request, context):
        self.publish_job(name, request)
        return jobs_pb2.JobResponse(status='OK')

    def remove_job(self, job_id):
        return remove_job(job_id)

    def _extract_args(self, command: StartCommand, request):
        args = {}
        for arg_name in [arg.name for arg in command.args] + ['user']:
            attr = request.get(arg_name) if isinstance(request, dict) else getattr(request, arg_name, None)
            if attr is not None:
                args[arg_name] = attr
        return args
