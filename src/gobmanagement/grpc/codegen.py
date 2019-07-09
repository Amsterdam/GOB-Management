"""
Generates proto definition based on start_commands in gobcore.
Generates python code for proto/gobmanagement.proto
"""
import os

from grpc_tools import protoc
from gobcore.workflow.start_commands import StartCommands

from typing import TextIO

PROTO_NAME = 'jobs'
PROTOS_DIR = 'protos'
PROTOC_OUT_DIR = 'out'

PACKAGE_PREFIX = 'gobmanagement.grpc.out'
PROTO_LOCATION = f'{PROTOS_DIR}/{PROTO_NAME}.proto'


class GRPCCodeGenerator:
    """Generates the gRPC Proto definition based on the start commands definition in GOB Core. Uses the generated
    proto definition with the protoc compiler to generate the Python boilerplate code.
    """

    def __init__(self):
        self.messages = []
        self.services = []

    def _collect_commands(self):
        """Populates self.messages and self.services based on the start commands definition.

        :return:
        """
        commands = StartCommands()
        response_message = 'JobResponse'

        for _, command in commands.get_all().items():
            args = [{'name': arg.name, 'type': 'string'} for arg in command.args]
            command_name = command.name.capitalize()
            message_name = f"{command_name}Job"

            self.services.append({
                'name': f"Start{command_name}Job",
                'arg': message_name,
                'ret': response_message,
            })

            self.messages.append({
                'name': message_name,
                'args': args,
            })

        self.messages.append({
            'name': response_message,
            'args': [{'name': 'status', 'type': 'string'}]
        })

    def _write_header(self, fp: TextIO):
        """Writes proto definition header to fp

        :param fp:
        :return:
        """
        fp.writelines([
            'syntax = "proto3";\n\n',
        ])

    def _write_services(self, fp: TextIO):
        """Writes service definitions to fp

        :param fp:
        :return:
        """
        service_lines = [f"\trpc {service['name']}({service['arg']}) returns ({service['ret']}) {{}}\n"
                         for service in self.services]

        fp.writelines([
            'service Jobs {\n',
            *service_lines,
            '}\n\n'
        ])

    def _write_messages(self, fp: TextIO):
        """Writes message definitions to fp

        :param fp:
        :return:
        """
        for message in self.messages:
            self._write_message(fp, message)

    def _write_message(self, fp: TextIO, message: dict):
        """Writes single message to fp

        :param fp:
        :param message:
        :return:
        """
        arg_lines = [f"\t{arg['type']} {arg['name']} = {i + 1};\n" for i, arg in enumerate(message['args'])]

        fp.writelines([
            f"message {message['name']} {{\n",
            *arg_lines,
            "}\n\n"
        ])

    def generate_proto_definition(self):
        """Writes gRPC proto definition to file PROTO_LOCATION

        :return:
        """
        with open(self._absolute_path(PROTO_LOCATION), 'w') as fp:
            self._write_header(fp)
            self._write_services(fp)
            self._write_messages(fp)

    def compile_proto(self):
        """Compiles gRPC proto definition in PROTO_LOCATION to Python code

        :return:
        """
        protoc.main((
            '',
            f'-I{self._absolute_path(PROTOS_DIR)}',
            f'--python_out={self._absolute_path(PROTOC_OUT_DIR)}',
            f'--grpc_python_out={self._absolute_path(PROTOC_OUT_DIR)}',
            f'{self._absolute_path(PROTO_LOCATION)}'
        ))

        self._fix_import()

    def _fix_import(self):
        """Fixes the import in the protoc compiler result files. Import is relative to the out directory. This method
        changes the imports relative to the gobmanagement package.

        :return:
        """
        filename = self._absolute_path(os.path.join(PROTOC_OUT_DIR, f'{PROTO_NAME}_pb2_grpc.py'))

        with open(filename, 'r') as f:
            old_contents = f.read()

        new_contents = old_contents.replace(f'import {PROTO_NAME}_pb2', f'import {PACKAGE_PREFIX}.{PROTO_NAME}_pb2')

        with open(filename, 'w') as f:
            f.write(new_contents)

    def _absolute_path(self, relative_path: str):
        """Returns the absolute path for relative_path (relative to this file)

        :param relative_path:
        :return:
        """
        return os.path.join(os.path.abspath(os.path.dirname(__file__)), relative_path)

    def generate(self):
        """Entry method. Generates proto definition and compiles it.

        :return:
        """
        self._collect_commands()
        self.generate_proto_definition()
        self.compile_proto()


generator = GRPCCodeGenerator()
generator.generate()
