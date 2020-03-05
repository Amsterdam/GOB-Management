from unittest import TestCase, mock
from unittest.mock import MagicMock

from gobmanagement.schemas import ServiceConnection, MsgCategory, SourceEntity

class TestSchema(TestCase):

    def test_service_connection(self):
        sc = ServiceConnection(None)
        self.assertIsNotNone(sc)

    def test_msg_category(self):
        mc = MsgCategory(None, None)
        self.assertIsNotNone(mc)

    def test_source_entity(self):
        se = SourceEntity(None, None, None)
        self.assertIsNotNone(se)
