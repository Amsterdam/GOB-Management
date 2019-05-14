from unittest.mock import MagicMock
import types

import pytest

from gobmanagement.database import base


def test_session_scope_rw():
    session_mock = MagicMock()
    with base.session_scope(backend=lambda: session_mock) as session:
        assert not isinstance(session_mock.flush, types.LambdaType)
    session_mock.commit.assert_called()
    session_mock.close.assert_called()

def test_session_scope_ro():
    session_mock = MagicMock()
    with base.session_scope(True, backend=lambda: session_mock) as session:
        assert isinstance(session.flush, types.LambdaType)
    session_mock.commit.assert_not_called()
    session_mock.close.assert_called()

def test_session_scope_exc():
    session_mock = MagicMock()
    with pytest.raises(Exception):
        with base.session_scope(backend=lambda: session_mock) as session:
            raise RuntimeError
    session_mock.commit.assert_not_called()
    session_mock.rollback.assert_called()