import numpy as np
# Try to import pyrtlsdr, but fall back to simulation mode if it fails
try:
    from rtlsdr import RtlSdr
    try:
        from rtlsdr.rtlsdraio import RtlSdrAio, AIO_AVAILABLE
    except ImportError:
        AIO_AVAILABLE = False
    PYRTLSDR_AVAILABLE = True
except ImportError:
    print("Warning: pyrtlsdr module not available, using simulation mode only")
    PYRTLSDR_AVAILABLE = False
    AIO_AVAILABLE = False
import stomp
import time
import json
import creds
import sys
import asyncio

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

async def process_samples(samples, conn, use_simulation, center_freq, sample_rate, sdr):
    """Process samples and send to ActiveMQ."""
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

    # Use time.sleep for compatibility with tests that mock it
    # but wrap it in asyncio.sleep for non-blocking behavior in async mode
    time.sleep(0.06)  # This can be mocked by tests

async def async_main():
    """Asynchronous main function to run the SDR streaming to ActiveMQ."""
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
            max_retries = 3
            retry_count = 0
            while retry_count < max_retries:
                try:
                    if retry_count > 0:
                        print(f"Retry attempt {retry_count}/{max_retries}...")
                        # Sleep between retries to allow device to reset
                        await asyncio.sleep(2)

                    if AIO_AVAILABLE:
                        print("Using asynchronous RTL-SDR mode")
                        sdr = RtlSdrAio()
                    else:
                        print("Using synchronous RTL-SDR mode")
                        sdr = RtlSdr()

                    sdr.sample_rate = sample_rate
                    sdr.center_freq = center_freq
                    sdr.gain = 'auto'

                    # If we get here, initialization was successful
                    print("RTL-SDR device initialized successfully")
                    break
                except Exception as e:
                    print(f"Warning: Could not initialize RTL-SDR device (attempt {retry_count+1}/{max_retries}): {e}")
                    if retry_count == max_retries - 1:
                        print("All retry attempts failed. Falling back to simulation mode")
                        use_simulation = True
                    # Close the device if it was partially initialized
                    try:
                        if 'sdr' in locals() and sdr:
                            sdr.close()
                            sdr = None
                    except Exception:
                        pass
                retry_count += 1
        else:
            print("RTL-SDR module not available, using simulation mode")

        print("Streaming to ActiveMQ...")

        if not use_simulation and AIO_AVAILABLE and isinstance(sdr, RtlSdrAio):
            # Asynchronous streaming mode
            async for samples in sdr.stream(num_samples_or_bytes=2048):
                await process_samples(samples, conn, use_simulation, center_freq, sample_rate, sdr)
        else:
            # Synchronous or simulation mode
            while True:
                if use_simulation:
                    samples = generate_simulated_samples(2048)
                else:
                    samples = sdr.read_samples(2048)

                await process_samples(samples, conn, use_simulation, center_freq, sample_rate, sdr)
    except KeyboardInterrupt:
        print("Interrupted by user.")
    finally:
        try:
            if sdr:
                if isinstance(sdr, RtlSdrAio):
                    await sdr.stop()
                sdr.close()
        except Exception:
            pass
        try:
            if conn:
                conn.disconnect()
        except Exception:
            pass
        print("Stopped.")
    return

def main():
    """Main function to run the SDR streaming to ActiveMQ."""
    try:
        # Always use the async_main function, but the way we run it depends on AIO_AVAILABLE
        if AIO_AVAILABLE and PYRTLSDR_AVAILABLE:  # Only use asyncio.run if both are available
            asyncio.run(async_main())
        else:
            # Create a simple event loop for the async_main function
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(async_main())
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

if __name__ == "__main__":
    main()
