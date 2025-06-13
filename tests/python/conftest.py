# tests/python/conftest.py
import os
import pytest
from unittest.mock import MagicMock

@pytest.fixture
def mock_env():
    """Set up test environment variables."""
    original_env = os.environ.copy()
    
    # Clear relevant environment variables
    for var in ['ACTIVEMQ_HOST', 'ACTIVEMQ_PORT', 'ACTIVEMQ_DEST', 'ACTIVEMQ_USER', 'ACTIVEMQ_PASS']:
        if var in os.environ:
            del os.environ[var]
    
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)

@pytest.fixture
def mock_stomp_connection(mocker):
    """Create a mock STOMP connection."""
    mock_conn = MagicMock()
    mocker.patch('stomp.Connection', return_value=mock_conn)
    return mock_conn

@pytest.fixture
def mock_datetime(mocker):
    """Mock the datetime module."""
    mock_dt = mocker.patch('datetime.datetime')
    mock_dt.utcnow.return_value.isoformat.return_value = '2023-01-01T12:00:00'
    return mock_dt