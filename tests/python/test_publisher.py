# tests/python/test_publisher.py
import datetime
import time
import pytest
from unittest.mock import MagicMock, patch

# Import the module to test
import publisher

@pytest.fixture
def mock_stomp_connection(mocker):
    """Create a mock STOMP connection."""
    mock_conn = MagicMock()
    mocker.patch('stomp.Connection', return_value=mock_conn)
    return mock_conn

@pytest.fixture
def mock_creds(mocker):
    """Mock the creds module."""
    mock_creds = mocker.patch('publisher.creds')
    mock_creds.BROKER = [('localhost', 61613)]
    mock_creds.USER = 'test_user'
    mock_creds.PASS = 'test_pass'
    mock_creds.DEST = '/queue/test'
    return mock_creds

def test_connection_setup(mock_stomp_connection, mock_creds):
    """Test that the STOMP connection is set up correctly."""
    # Call the function that sets up the connection
    with patch('time.sleep', side_effect=KeyboardInterrupt):  # Break the loop
        publisher.main()  # KeyboardInterrupt is caught inside main()

    # Verify the connection was created with the correct parameters
    # The mock is already set up in the fixture, so we don't need to verify the call to stomp.Connection

    # Verify connect was called with the correct credentials
    mock_stomp_connection.connect.assert_called_once_with(
        login=mock_creds.USER, 
        passcode=mock_creds.PASS, 
        wait=True
    )

def test_message_sending(mock_stomp_connection, mock_creds, mocker):
    """Test that messages are sent correctly."""
    # Mock datetime to return a fixed time
    fixed_time = '2023-01-01T12:00:00Z'
    mock_datetime = mocker.patch('publisher.datetime')
    mock_datetime.datetime.utcnow.return_value.isoformat.return_value = fixed_time[:-1]  # Without Z

    # Mock time.sleep to raise KeyboardInterrupt after one iteration
    mock_sleep = mocker.patch('time.sleep', side_effect=[None, KeyboardInterrupt])

    # Call the main function
    publisher.main()  # KeyboardInterrupt is caught inside main()

    # Verify a message was sent with the correct parameters
    mock_stomp_connection.send.assert_called_with(
        destination=mock_creds.DEST,
        body=fixed_time,
        headers={'content-type': 'text/plain'}
    )

def test_disconnect_on_keyboard_interrupt(mock_stomp_connection, mock_creds):
    """Test that the connection is disconnected on KeyboardInterrupt."""
    # Mock time.sleep to raise KeyboardInterrupt
    with patch('time.sleep', side_effect=KeyboardInterrupt):
        publisher.main()  # KeyboardInterrupt is caught inside main()

    # Verify disconnect was called
    mock_stomp_connection.disconnect.assert_called_once()

def test_disconnect_on_exception(mock_stomp_connection, mock_creds, mocker):
    """Test that the connection is disconnected on any exception."""
    # Mock time.sleep to raise an exception
    mock_sleep = mocker.patch('time.sleep', side_effect=Exception("Test exception"))

    # Call the main function
    with pytest.raises(Exception, match="Test exception"):
        publisher.main()

    # Verify disconnect was called
    mock_stomp_connection.disconnect.assert_called_once()
