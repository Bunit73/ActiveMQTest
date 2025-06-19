#!/usr/bin/env python
"""
SDR Data Console Printer and ActiveMQ Publisher

This script initializes an RTL-SDR dongle, reads data from it, processes the data,
and sends the results to ActiveMQ. It also prints the data to the console.
It requires the pyrtlsdr, numpy, stomp.py, and python-dotenv libraries to be installed.

Usage:
    python sdr.py
"""

import sys
import time
import json
import numpy as np
import stomp
import random
from math import log10

# Check if pyrtlsdr is available
PYRTLSDR_AVAILABLE = True
try:
    from rtlsdr import RtlSdr
except ImportError:
    PYRTLSDR_AVAILABLE = False
    print("Warning: pyrtlsdr module not available. Running in simulation mode.")

# Import ActiveMQ connection settings
try:
    from creds import BROKER, USER, PASS, SDR_DEST
except ImportError:
    # Fallback if creds.py is not available
    import os
    from dotenv import load_dotenv

    # Load environment variables from .env file (if present)
    load_dotenv()

    # Get ActiveMQ connection settings from environment variables
    BROKER = [(
        os.getenv('ACTIVEMQ_HOST', 'localhost'),
        int(os.getenv('ACTIVEMQ_PORT', '61613'))
    )]
    USER = os.getenv('ACTIVEMQ_USER', 'admin')
    PASS = os.getenv('ACTIVEMQ_PASS', 'admin')
    SDR_DEST = os.getenv('ACTIVEMQ_SDR_DEST', '/queue/sdr')

# ActiveMQ listener class
class MyListener(stomp.ConnectionListener):
    def on_error(self, headers, message):
        print('ActiveMQ error:', message)
    def on_connected(self, headers):
        print("Connected to ActiveMQ")

def setup_activemq():
    """
    Initialize and configure the ActiveMQ connection.

    Returns:
        stomp.Connection: Configured ActiveMQ connection object
    """
    try:
        print(f"\n=== ActiveMQ Connection Information ===")
        print(f"Connecting to ActiveMQ at {BROKER}...")
        conn = stomp.Connection(host_and_ports=BROKER, heartbeats=(0, 0))
        conn.set_listener('', MyListener())
        conn.connect(login=USER, passcode=PASS, wait=True)
        print(f"Connected to ActiveMQ")
        print(f"Destination: {SDR_DEST}")
        return conn
    except Exception as e:
        print(f"Error connecting to ActiveMQ: {e}")
        return None

def compute_fft(samples, log_scale=True):
    """
    Compute the FFT of the samples and convert to power in dB.

    Args:
        samples (numpy.ndarray): Complex samples from SDR
        log_scale (bool): Whether to convert to logarithmic (dB) scale

    Returns:
        numpy.ndarray: Power spectrum in dB
    """
    # Compute FFT
    fft = np.fft.fft(samples)

    # Shift the FFT so that the center frequency is in the middle
    fft_shifted = np.fft.fftshift(fft)

    # Calculate power (magnitude squared)
    power = np.abs(fft_shifted) ** 2

    # Convert to dB scale if requested
    if log_scale:
        # Add a small value to avoid log(0)
        power_db = 10 * np.log10(power + 1e-10)
        return power_db
    else:
        return power

def generate_simulated_samples(size=1024, center_freq=100e6, sample_rate=2.048e6):
    """
    Generate simulated complex samples for testing when no SDR hardware is available.

    Args:
        size (int): Number of samples to generate
        center_freq (float): Center frequency in Hz
        sample_rate (float): Sample rate in Hz

    Returns:
        numpy.ndarray: Complex samples
    """
    # Generate random complex samples
    real_part = np.random.normal(0, 1, size)
    imag_part = np.random.normal(0, 1, size)
    samples = real_part + 1j * imag_part

    # Add some peaks to simulate signals
    num_peaks = random.randint(1, 5)
    for _ in range(num_peaks):
        # Random position for the peak
        peak_pos = random.randint(0, size-1)
        # Random strength for the peak
        peak_strength = random.uniform(5, 20)
        # Add the peak
        samples[peak_pos] += peak_strength * (1 + 1j)

    return samples

def send_to_activemq(conn, message_data, message_type="sample", spectrum_data=None, center_freq=100e6, sample_rate=2.048e6, simulated=False):
    """
    Send data to ActiveMQ.

    Args:
        conn (stomp.Connection): ActiveMQ connection object
        message_data (dict): Data to send
        message_type (str): Type of message (sample, summary, etc.)
        spectrum_data (numpy.ndarray, optional): Spectrum data to include
        center_freq (float): Center frequency in Hz
        sample_rate (float): Sample rate in Hz
        simulated (bool): Whether the data is simulated

    Returns:
        bool: True if successful, False otherwise
    """
    if conn is None:
        print("ActiveMQ connection not available")
        return False

    try:
        # Add message metadata
        message = {
            'timestamp': time.time(),
            'type': message_type,
            'data': message_data,
            'center_freq': center_freq,
            'sample_rate': sample_rate,
            'simulated': simulated
        }

        # Add spectrum data if provided
        if spectrum_data is not None and len(spectrum_data) > 0:
            # Convert to Python list for JSON serialization
            message['spectrum_db'] = spectrum_data.tolist()

        # Send message
        conn.send(destination=SDR_DEST, body=json.dumps(message))
        return True
    except Exception as e:
        print(f"Error sending to ActiveMQ: {e}")
        return False

def setup_sdr():
    """
    Initialize and configure the RTL-SDR device.

    Returns:
        RtlSdr: Configured RTL-SDR device object
    """
    try:
        sdr = RtlSdr()

        # Configure SDR settings
        sdr.sample_rate = 2.048e6  # Hz
        sdr.center_freq = 100e6    # Hz (adjust to a frequency of interest, e.g., FM radio)
        sdr.freq_correction = 60   # PPM
        sdr.gain = 'auto'

        # Print comprehensive SDR device information
        print("\n=== SDR Device Information ===")
        try:
            print(f"Device index: {sdr.device_index}")
        except AttributeError:
            print("Device index: Not available")
        try:
            print(f"Device name: {sdr.get_device_name()}")
        except AttributeError:
            print("Device name: Not available")

        try:
            print(f"Manufacturer: {sdr.get_manufacturer()}")
        except AttributeError:
            print("Manufacturer: Not available")

        try:
            print(f"Product: {sdr.get_product()}")
        except AttributeError:
            print("Product: Not available")

        try:
            print(f"Serial number: {sdr.get_serial_number()}")
        except AttributeError:
            print("Serial number: Not available")

        try:
            print(f"Tuner type: {sdr.get_tuner_type()}")
        except AttributeError:
            print("Tuner type: Not available")

        # Print configuration information
        print("\n=== SDR Configuration ===")
        print(f"Sample rate: {sdr.sample_rate / 1e6} MHz")
        print(f"Center frequency: {sdr.center_freq / 1e6} MHz")
        print(f"Frequency correction: {sdr.freq_correction} PPM")
        print(f"Gain: {sdr.gain} dB")

        try:
            gains = sdr.get_gains()
            print(f"Available gain values: {', '.join([str(g) for g in gains])} dB")
        except AttributeError:
            print("Available gain values: Not available")

        try:
            print(f"Direct sampling mode: {sdr.direct_sampling}")
        except AttributeError:
            print("Direct sampling mode: Not available")

        try:
            print(f"Bandwidth: {sdr.get_bandwidth()} Hz")
        except AttributeError:
            print("Bandwidth: Not available")

        return sdr
    except Exception as e:
        print(f"Error initializing SDR: {e}")
        sys.exit(1)

def read_and_print_samples(sdr, activemq_conn=None, num_samples=1024, simulated=False):
    """
    Read samples from the SDR device, print them to the console, and send to ActiveMQ.
    Runs continuously until interrupted by the user.

    Args:
        sdr (RtlSdr): Configured RTL-SDR device
        activemq_conn (stomp.Connection): ActiveMQ connection object
        num_samples (int): Number of samples to read at once
        simulated (bool): Whether to use simulated data
    """
    try:
        print("\n=== SDR Signal Information ===")
        print(f"Reading samples continuously. Press Ctrl+C to stop...")

        # Get device parameters
        if sdr and not simulated:
            center_freq = sdr.center_freq
            sample_rate = sdr.sample_rate
        else:
            center_freq = 100e6  # Default center frequency
            sample_rate = 2.048e6  # Default sample rate

        # Track statistics across all reads
        all_powers = []
        read_count = 0

        while True:  # Run indefinitely until interrupted
            read_count += 1
            # Read samples (or generate simulated samples)
            if simulated:
                samples = generate_simulated_samples(num_samples, center_freq, sample_rate)
                print("Using simulated samples")
            else:
                samples = sdr.read_samples(num_samples)

            # Convert to power (magnitude squared)
            power = np.abs(samples) ** 2
            all_powers.extend(power)

            # Calculate statistics
            mean_power = np.mean(power)
            max_power = np.max(power)
            min_power = np.min(power)
            median_power = np.median(power)
            std_dev = np.std(power)

            # Calculate signal quality metrics
            snr_estimate = mean_power / std_dev if std_dev > 0 else 0

            # Compute FFT and get spectrum data in dB
            spectrum_db = compute_fft(samples)

            # Calculate frequency domain information
            try:
                # Use the FFT to find peak frequency
                fft = np.fft.fft(samples)
                fft_freq = np.fft.fftfreq(len(samples), 1/sample_rate)
                fft_power = np.abs(fft)**2
                peak_freq_idx = np.argmax(fft_power[:len(fft_power)//2])
                peak_freq = fft_freq[peak_freq_idx]
                peak_power = fft_power[peak_freq_idx]

                has_fft_data = True
            except Exception as e:
                print(f"Error calculating frequency domain info: {e}")
                has_fft_data = False

            # Prepare data for ActiveMQ
            sample_data = {
                'read_number': read_count,
                'total_reads': None,
                'sample_count': len(samples),
                'time_domain': {
                    'mean_power': float(mean_power),
                    'median_power': float(median_power),
                    'max_power': float(max_power),
                    'min_power': float(min_power),
                    'std_dev': float(std_dev),
                    'snr_estimate': float(snr_estimate)
                },
                'first_samples': [{'real': float(s.real), 'imag': float(s.imag)} for s in samples[:10]]
            }

            # Add frequency domain data if available
            if has_fft_data:
                sample_data['frequency_domain'] = {
                    'peak_freq_mhz': float(peak_freq/1e6),
                    'peak_power': float(peak_power)
                }

            # Send data to ActiveMQ
            if activemq_conn:
                send_success = send_to_activemq(
                    activemq_conn, 
                    sample_data, 
                    "sample", 
                    spectrum_db, 
                    center_freq, 
                    sample_rate, 
                    simulated
                )
                if send_success:
                    print(f"\n--- Read #{read_count} --- (Sent to ActiveMQ)")
                else:
                    print(f"\n--- Read #{read_count} --- (Failed to send to ActiveMQ)")
            else:
                print(f"\n--- Read #{read_count} ---")

            print(f"Number of samples: {len(samples)}")

            print("\nTime Domain Analysis:")
            print(f"  Mean power: {mean_power:.6f}")
            print(f"  Median power: {median_power:.6f}")
            print(f"  Max power: {max_power:.6f}")
            print(f"  Min power: {min_power:.6f}")
            print(f"  Standard deviation: {std_dev:.6f}")
            print(f"  Estimated SNR: {snr_estimate:.6f}")

            if has_fft_data:
                print("\nFrequency Domain Analysis:")
                print(f"  Peak frequency: {peak_freq/1e6:.3f} MHz (relative to center)")
                print(f"  Peak power: {peak_power:.6f}")

            # Print first few samples
            print("\nSample values (first 10):")
            for j, sample in enumerate(samples[:10]):
                print(f"  Sample {j}: {sample.real:.6f} + {sample.imag:.6f}j")

            # Print summary statistics periodically (every 10 reads)
            if read_count % 10 == 0 and all_powers:
                print("\n=== SDR Signal Summary (Last 100 Reads or Less) ===")

                # Limit the statistics to the last 100 reads to avoid memory growth
                if len(all_powers) > 100 * num_samples:
                    all_powers = all_powers[-100 * num_samples:]

                all_mean = np.mean(all_powers)
                all_median = np.median(all_powers)
                all_max = np.max(all_powers)
                all_min = np.min(all_powers)
                all_std = np.std(all_powers)
                all_snr = all_mean / all_std if all_std > 0 else 0

                # Prepare summary data for ActiveMQ
                summary_data = {
                    'total_samples': len(all_powers),
                    'overall_mean_power': float(all_mean),
                    'overall_median_power': float(all_median),
                    'overall_max_power': float(all_max),
                    'overall_min_power': float(all_min),
                    'overall_std_dev': float(all_std),
                    'overall_snr': float(all_snr)
                }

                # Send summary to ActiveMQ
                if activemq_conn:
                    # Compute a final spectrum for the summary
                    if simulated:
                        final_samples = generate_simulated_samples(num_samples, center_freq, sample_rate)
                    else:
                        try:
                            final_samples = sdr.read_samples(num_samples)
                        except Exception:
                            final_samples = None

                    if final_samples is not None:
                        final_spectrum = compute_fft(final_samples)
                    else:
                        final_spectrum = None

                    send_success = send_to_activemq(
                        activemq_conn, 
                        summary_data, 
                        "summary", 
                        final_spectrum, 
                        center_freq, 
                        sample_rate, 
                        simulated
                    )
                    if send_success:
                        print("Summary statistics sent to ActiveMQ")
                    else:
                        print("Failed to send summary statistics to ActiveMQ")

                print(f"Total samples analyzed: {len(all_powers)}")
                print(f"Overall mean power: {all_mean:.6f}")
                print(f"Overall median power: {all_median:.6f}")
                print(f"Overall max power: {all_max:.6f}")
                print(f"Overall min power: {all_min:.6f}")
                print(f"Overall standard deviation: {all_std:.6f}")
                print(f"Overall estimated SNR: {all_snr:.6f}")

    except KeyboardInterrupt:
        print("\nSampling interrupted by user")
    except Exception as e:
        print(f"\nError reading samples: {e}")

def main():
    """
    Main function to run the SDR data console printer and ActiveMQ publisher.
    The program runs continuously until interrupted by the user (Ctrl+C).
    """
    print("SDR Data Console Printer and ActiveMQ Publisher")
    print("----------------------------------------------")

    # Initialize ActiveMQ connection
    activemq_conn = setup_activemq()

    # Check if pyrtlsdr is available
    if not PYRTLSDR_AVAILABLE:
        print("\n=== Running in Simulation Mode ===")
        print("pyrtlsdr module is not available. Using simulated data.")

        try:
            # Read, print, and send simulated samples continuously
            read_and_print_samples(None, activemq_conn, simulated=True)
        finally:
            # Disconnect from ActiveMQ
            if activemq_conn:
                print("\nDisconnecting from ActiveMQ...")
                activemq_conn.disconnect()
                print("Disconnected from ActiveMQ")
        return

    # Try to initialize SDR
    try:
        sdr = setup_sdr()
    except Exception as e:
        print(f"\n=== Running in Simulation Mode ===")
        print(f"Failed to initialize SDR: {e}")
        print("Using simulated data instead.")

        try:
            # Read, print, and send simulated samples continuously
            read_and_print_samples(None, activemq_conn, simulated=True)
        finally:
            # Disconnect from ActiveMQ
            if activemq_conn:
                print("\nDisconnecting from ActiveMQ...")
                activemq_conn.disconnect()
                print("Disconnected from ActiveMQ")
        return

    # If we got here, we have a working SDR
    try:
        # Read, print, and send samples continuously
        read_and_print_samples(sdr, activemq_conn)
    finally:
        # Clean up
        if sdr:
            print("\nClosing SDR device...")
            sdr.close()
            print("SDR device closed")

        # Disconnect from ActiveMQ
        if activemq_conn:
            print("\nDisconnecting from ActiveMQ...")
            activemq_conn.disconnect()
            print("Disconnected from ActiveMQ")

if __name__ == "__main__":
    main()
