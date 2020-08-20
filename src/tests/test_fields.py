from unittest import TestCase
from unittest.mock import MagicMock, patch

from gobmanagement.fields import LogFilterConnectionField


class TestLogFilterConnectionField(TestCase):

    @patch("gobmanagement.fields.SQLAlchemyConnectionField.get_query")
    def test_get_query(self, mock_get_query):
        model = type('MockModel', (), {
            'level': type('NotLike', (), {
                'notlike': lambda x: 'not like ' + x
            })
        })

        res = LogFilterConnectionField.get_query(model, MagicMock())
        mock_get_query.return_value.filter.assert_called_with('not like DATA%')
        self.assertEqual(mock_get_query().filter(), res)
