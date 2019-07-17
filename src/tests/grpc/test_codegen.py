from unittest import TestCase
from unittest.mock import patch, MagicMock, Mock, call, mock_open

from gobmanagement.grpc.codegen import GRPCCodeGenerator, PROTO_LOCATION, PROTO_NAME, PROTOC_OUT_DIR, PROTOS_DIR


class TestGRPCCodeGenerator(TestCase):

    @patch("gobmanagement.grpc.codegen.StartCommands")
    def test_collect_commands(self, mock_start_commands):
        class MockArg:
            def __init__(self, name: str):
                self.name = name

        class MockCommand:
            def __init__(self, name: str, args: list):
                self.name = name
                self.args = [MockArg(arg) for arg in args]

        mock_start_commands.return_value.get_all.return_value = {
            'command_a': MockCommand('command_a', ['a', 'b', 'c']),
            'command_b': MockCommand('command_b', ['d', 'e', 'f']),
        }

        generator = GRPCCodeGenerator()
        generator._collect_commands()

        self.assertEqual([{
            'name': 'StartCommand_aJob',
            'arg': 'Command_aJob',
            'ret': 'JobResponse',
        }, {
            'name': 'StartCommand_bJob',
            'arg': 'Command_bJob',
            'ret': 'JobResponse',
        }], generator.services)

        self.assertEqual([{
            'name': 'Command_aJob',
            'args': [
                {'name': 'a', 'type': 'string'},
                {'name': 'b', 'type': 'string'},
                {'name': 'c', 'type': 'string'},
            ]
        }, {
            'name': 'Command_bJob',
            'args': [
                {'name': 'd', 'type': 'string'},
                {'name': 'e', 'type': 'string'},
                {'name': 'f', 'type': 'string'},
            ]
        }, {
            'name': 'JobResponse',
            'args': [
                {'name': 'status', 'type': 'string'}
            ]
        }], generator.messages)

    class MockFp:
        def __init__(self):
            self.contents = ""

        def writelines(self, lines):
            self.contents += ''.join(lines)

    def test_write_header(self):
        fp = self.MockFp()
        generator = GRPCCodeGenerator()
        generator._write_header(fp)

        self.assertEqual('syntax = "proto3";\n\n', fp.contents)

    def test_write_services(self):
        fp = self.MockFp()
        generator = GRPCCodeGenerator()
        generator.services = [{'name': 'ServiceName', 'arg': 'ARG', 'ret': 'ReturnObject'}]
        generator._write_services(fp)

        self.assertEqual('service Jobs {\n\trpc ServiceName(ARG) returns (ReturnObject) {}\n}\n\n', fp.contents)

    def test_write_messages(self):
        fp = self.MockFp()
        generator = GRPCCodeGenerator()
        generator.messages = [{'name': 'MessageName', 'args': [
            {'type': 'argType', 'name': 'argName'},
            {'type': 'argType2', 'name': 'argName2'}
        ]}]
        generator._write_messages(fp)

        self.assertEqual('message MessageName {\n\targType argName = 1;\n\targType2 argName2 = 2;\n}\n\n', fp.contents)

    @patch('builtins.open')
    def test_generate_proto_definition(self, mock_open):
        generator = GRPCCodeGenerator()
        generator._write_header = MagicMock()
        generator._write_services = MagicMock()
        generator._write_messages = MagicMock()
        generator._absolute_path = lambda x: 'abs_' + x

        manager = Mock()
        manager.attach_mock(generator._write_header, '_write_header')
        manager.attach_mock(generator._write_services, '_write_services')
        manager.attach_mock(generator._write_messages, '_write_messages')

        generator.generate_proto_definition()
        mock_open.assert_called_with('abs_' + PROTO_LOCATION, 'w')

        self.assertEqual([
            call._write_header(mock_open.return_value.__enter__.return_value),
            call._write_services(mock_open.return_value.__enter__.return_value),
            call._write_messages(mock_open.return_value.__enter__.return_value),
        ], manager.mock_calls)

    @patch('gobmanagement.grpc.codegen.protoc.main')
    def test_compile_proto(self, mock_protoc_main):
        generator = GRPCCodeGenerator()
        generator._fix_import = MagicMock()
        generator._absolute_path = lambda x: 'abs_' + x

        generator.compile_proto()
        mock_protoc_main.assert_called_with((
            '',
            '-Iabs_' + PROTOS_DIR,
            '--python_out=abs_' + PROTOC_OUT_DIR,
            '--grpc_python_out=abs_' + PROTOC_OUT_DIR,
            'abs_' + PROTO_LOCATION
        ))

        generator._fix_import.assert_called_once()

    @patch('builtins.open')
    @patch('os.path.join')
    def test_fix_import(self, mock_join, mock_open):
        generator = GRPCCodeGenerator()
        generator._absolute_path = lambda x: 'abs_' + x
        mock_join.return_value = 'joined_path'
        old_content = f'some text and import {PROTO_NAME}_pb2 and some more stuff'
        mock_open.return_value.__enter__.return_value.read.return_value = old_content

        generator._fix_import()

        mock_join.assert_called_with(PROTOC_OUT_DIR, f'{PROTO_NAME}_pb2_grpc.py')
        mock_open.assert_any_call('abs_joined_path', 'r')
        mock_open.assert_any_call('abs_joined_path', 'w')

        # Write back replaced content
        mock_open.return_value.__enter__.return_value.write.assert_called_with(
            f'some text and import gobmanagement.grpc.out.{PROTO_NAME}_pb2 and some more stuff'
        )

    def test_generate(self):
        generator = GRPCCodeGenerator()
        generator._collect_commands = MagicMock()
        generator.generate_proto_definition = MagicMock()
        generator.compile_proto = MagicMock()

        manager = Mock()
        manager.attach_mock(generator._collect_commands, '_collect_commands')
        manager.attach_mock(generator.generate_proto_definition, 'generate_proto_definition')
        manager.attach_mock(generator.compile_proto, 'compile_proto')

        generator.generate()

        self.assertEqual([
            call._collect_commands(),
            call.generate_proto_definition(),
            call.compile_proto()
        ], manager.mock_calls)

    @patch('os.path.join', lambda x, y: 'joined_path(' + x + ' and ' + y + ')')
    @patch('os.path.abspath', lambda x: 'abs(' + x + ')')
    @patch('os.path.dirname', lambda x: 'dirname()')
    def test_absolute_path(self):
        generator = GRPCCodeGenerator()
        res = generator._absolute_path('rel_path')

        self.assertEqual('joined_path(abs(dirname()) and rel_path)', res)
