import numpy as np
# Try to import pyrtlsdr, but fall back to simulation mode if it fails
try:
    from pyrtlsdr import RtlSdr
    PYRTLSDR_AVAILABLE = True
except ImportError:
    print("Warning: pyrtlsdr module not available, using simulation mode only")
    PYRTLSDR_AVAILABLE = False
import stomp
import time
import json
import creds
import sys

# ActiveMQ listener class
class MyListener(stomp.ConnectionListener):
    def on_error(self, headers, message):
        print('ActiveMQ error:', message)
    def on_connected(self, headers):
        print("Connected to ActiveMQ")

def compute_fft(samples):
    """Compute FFT of samples and convert to power in dB."""
    windowed = samples * np.hamming(len(samples))
    fft = np.fft.fftshift(np.fft.fft(windowed))
    power_db = 20 * np.log10(np.abs(fft) + 1e-6)
    return power_db

def generate_simulated_samples(size=2048):
    """Generate simulated samples when RTL-SDR device is not available."""
    # Create random noise with a simulated signal
    samples = np.random.normal(0, 0.5, size) + 0.5j * np.random.normal(0, 0.5, size)

    # Add a simulated signal peak
    center_idx = size // 2
    signal_width = size // 20
    for i in range(center_idx - signal_width, center_idx + signal_width):
        if 0 <= i < size:
            samples[i] += 2.0 * np.exp(-(i - center_idx)**2 / (2 * signal_width**2))

    return samples

def main():
    """Main function to run the SDR streaming to ActiveMQ."""
    conn = None
    sdr = None
    use_simulation = not PYRTLSDR_AVAILABLE
    sample_rate = 2.4e6
    center_freq = 162.475e6

    try:
        # Setup ActiveMQ connection
        print("Connecting to ActiveMQ...")
        conn = stomp.Connection(host_and_ports=creds.BROKER, heartbeats=(0, 0))
        conn.set_listener('', MyListener())
        conn.connect(login=creds.USER, passcode=creds.PASS, wait=True)

        # Initialize SDR if available
        if PYRTLSDR_AVAILABLE:
            print("Initializing RTL-SDR device...")
            try:
                sdr = RtlSdr()
                sdr.sample_rate = sample_rate
                sdr.center_freq = center_freq
                sdr.gain = 'auto'
            except Exception as e:
                print(f"Warning: Could not initialize RTL-SDR device: {e}")
                print("Falling back to simulation mode")
                use_simulation = True
        else:
            print("RTL-SDR module not available, using simulation mode")

        print("Streaming to ActiveMQ...")
        while True:
            if use_simulation:
                samples = generate_simulated_samples(2048)
            else:
                samples = sdr.read_samples(2048)

            spectrum = compute_fft(samples)

            # Downsample and convert to list for JSON
            spectrum_downsampled = spectrum[::8].tolist()

            msg = {
                'timestamp': time.time(),
                'center_freq': center_freq if use_simulation else sdr.center_freq,
                'sample_rate': sample_rate if use_simulation else sdr.sample_rate,
                'spectrum_db': spectrum_downsampled,
                'simulated': use_simulation
            }
            print(json.dumps(msg))
            conn.send(destination=creds.SDR_DEST, body=json.dumps(msg))
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("Interrupted by user.")
    except ImportError as e:
        print(f"Error: {e}")
        print("Make sure you have installed all required packages:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    except stomp.exception.ConnectFailedException as e:
        print(f"Error connecting to ActiveMQ: {e}")
        print(f"Make sure ActiveMQ is running at {creds.BROKER}")
        print(f"Check your credentials (USER: {creds.USER})")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        print("If this is a USB error, make sure the RTL-SDR device is properly connected.")
        print("If this is a connection error, make sure ActiveMQ is running.")
        sys.exit(1)
    finally:
        try:
            if sdr:
                sdr.close()
        except Exception:
            pass
        try:
            if conn:
                conn.disconnect()
        except Exception:
            pass
        print("Stopped.")

if __name__ == "__main__":
    main()
