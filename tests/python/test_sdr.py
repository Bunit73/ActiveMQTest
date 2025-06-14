# tests/python/test_sdr.py
import pytest
from unittest.mock import MagicMock, patch
import numpy as np
import json

# Import the module to test
import sdr

@pytest.fixture
def mock_stomp_connection(mocker):
    """Create a mock STOMP connection."""
    mock_conn = MagicMock()
    mocker.patch('stomp.Connection', return_value=mock_conn)
    return mock_conn

@pytest.fixture
def mock_creds(mocker):
    """Mock the creds module."""
    mock_creds = mocker.patch('sdr.creds')
    mock_creds.BROKER = [('localhost', 61613)]
    mock_creds.USER = 'test_user'
    mock_creds.PASS = 'test_pass'
    mock_creds.SDR_DEST = '/queue/sdr'
    return mock_creds

def test_compute_fft():
    """Test the compute_fft function."""
    # Create a test signal with multiple frequency components
    samples = np.zeros(1024, dtype=complex)

    # Add a strong spike at one position
    samples[256] = 10.0

    # Add some noise to create variation
    np.random.seed(42)  # For reproducibility
    noise = np.random.normal(0, 0.1, 1024) + 1j * np.random.normal(0, 0.1, 1024)
    samples += noise

    # Compute FFT
    power_db = sdr.compute_fft(samples)

    # Check that the result is a numpy array of the right size
    assert isinstance(power_db, np.ndarray)
    assert len(power_db) == len(samples)

    # Check that there's significant variation in the power values
    assert np.max(power_db) - np.min(power_db) > 10

def test_generate_simulated_samples():
    """Test the generate_simulated_samples function."""
    # Generate samples
    samples = sdr.generate_simulated_samples(size=1024)

    # Check that the result is a complex numpy array of the right size
    assert isinstance(samples, np.ndarray)
    assert samples.dtype == complex
    assert len(samples) == 1024

    # Check that the values have a reasonable magnitude
    magnitudes = np.abs(samples)
    assert np.mean(magnitudes) > 0
    assert np.max(magnitudes) < 10  # Should be well below this for normal random values

def test_connection_setup(mock_stomp_connection, mock_creds, mocker):
    """Test that the STOMP connection is set up correctly."""
    # Mock sys.exit to prevent the test from exiting
    mock_exit = mocker.patch('sys.exit')

    # Mock the RtlSdr class
    mocker.patch('sdr.PYRTLSDR_AVAILABLE', False)

    # Mock time.sleep to raise KeyboardInterrupt after one iteration
    mock_sleep = mocker.patch('time.sleep')
    mock_sleep.side_effect = KeyboardInterrupt()

    # Call the main function
    sdr.main()

    # Verify the connection was created with the correct parameters
    mock_stomp_connection.connect.assert_called_once_with(
        login=mock_creds.USER, 
        passcode=mock_creds.PASS, 
        wait=True
    )

def test_message_sending(mock_stomp_connection, mock_creds, mocker):
    """Test that messages are sent correctly."""
    # Mock sys.exit to prevent the test from exiting
    mock_exit = mocker.patch('sys.exit')

    # Mock the RtlSdr class
    mocker.patch('sdr.PYRTLSDR_AVAILABLE', False)

    # Mock time.time to return a fixed time
    fixed_time = 1609459200.0  # 2021-01-01 00:00:00 UTC
    mocker.patch('time.time', return_value=fixed_time)

    # Mock time.sleep to raise KeyboardInterrupt after one iteration
    mock_sleep = mocker.patch('time.sleep')
    mock_sleep.side_effect = KeyboardInterrupt()

    # Call the main function
    sdr.main()

    # Verify a message was sent with the correct parameters
    mock_stomp_connection.send.assert_called_once()
    args, kwargs = mock_stomp_connection.send.call_args

    assert kwargs['destination'] == mock_creds.SDR_DEST

    # Parse the JSON body and check its structure
    body = json.loads(kwargs['body'])
    assert 'timestamp' in body
    assert body['timestamp'] == fixed_time
    assert 'center_freq' in body
    assert 'sample_rate' in body
    assert 'spectrum_db' in body
    assert 'simulated' in body
    assert body['simulated'] is True

def test_disconnect_on_keyboard_interrupt(mock_stomp_connection, mock_creds, mocker):
    """Test that the connection is disconnected on KeyboardInterrupt."""
    # Mock sys.exit to prevent the test from exiting
    mock_exit = mocker.patch('sys.exit')

    # Mock the RtlSdr class
    mocker.patch('sdr.PYRTLSDR_AVAILABLE', False)

    # Mock time.sleep to raise KeyboardInterrupt
    mock_sleep = mocker.patch('time.sleep')
    mock_sleep.side_effect = KeyboardInterrupt()

    # Call the main function
    sdr.main()

    # Verify disconnect was called
    mock_stomp_connection.disconnect.assert_called_once()
