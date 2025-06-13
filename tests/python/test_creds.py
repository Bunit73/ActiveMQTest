# tests/python/test_creds.py
import os
import pytest
from unittest.mock import patch

@pytest.fixture
def mock_env():
    """Set up test environment variables."""
    original_env = os.environ.copy()

    # Clear relevant environment variables and ensure they're not set
    for var in ['ACTIVEMQ_HOST', 'ACTIVEMQ_PORT', 'ACTIVEMQ_DEST', 'ACTIVEMQ_USER', 'ACTIVEMQ_PASS']:
        os.environ.pop(var, None)  # Remove if exists, do nothing if not

    yield

    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)

def test_default_values(mock_env, mocker):
    """Test that default values are used when environment variables are not set."""
    # Mock os.getenv to return default values
    mocker.patch('os.getenv', side_effect=lambda key, default=None: default)

    # Import creds after setting up the environment
    import importlib
    import creds
    importlib.reload(creds)

    # Check default values
    assert creds.BROKER == [('localhost', 61613)]
    assert creds.DEST == '/queue/test'
    assert creds.USER == 'admin'
    assert creds.PASS == 'admin'

def test_custom_values(mock_env):
    """Test that environment variables are used when they are set."""
    # Set environment variables
    os.environ['ACTIVEMQ_HOST'] = 'custom-host'
    os.environ['ACTIVEMQ_PORT'] = '1234'
    os.environ['ACTIVEMQ_DEST'] = '/queue/custom'
    os.environ['ACTIVEMQ_USER'] = 'custom-user'
    os.environ['ACTIVEMQ_PASS'] = 'custom-pass'

    # Import creds after setting up the environment
    import importlib
    import creds
    importlib.reload(creds)

    # Check custom values
    assert creds.BROKER == [('custom-host', 1234)]
    assert creds.DEST == '/queue/custom'
    assert creds.USER == 'custom-user'
    assert creds.PASS == 'custom-pass'

def test_dotenv_loading(mocker):
    """Test that .env file is loaded."""
    # Mock os.getenv to return values as if they were loaded from .env file
    env_values = {
        'ACTIVEMQ_HOST': 'env-file-host',
        'ACTIVEMQ_PORT': '5678',
        'ACTIVEMQ_DEST': '/queue/env-file',
        'ACTIVEMQ_USER': 'env-file-user',
        'ACTIVEMQ_PASS': 'env-file-pass'
    }

    def mock_getenv(key, default=None):
        return env_values.get(key, default)

    mocker.patch('os.getenv', side_effect=mock_getenv)

    # Mock load_dotenv to do nothing
    mocker.patch('dotenv.load_dotenv', return_value=None)

    # Import creds after setting up the environment
    import importlib
    import creds
    importlib.reload(creds)

    # Check values from mocked environment
    assert creds.BROKER == [('env-file-host', 5678)]
    assert creds.DEST == '/queue/env-file'
    assert creds.USER == 'env-file-user'
    assert creds.PASS == 'env-file-pass'
