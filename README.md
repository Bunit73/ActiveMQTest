# ActiveMQ messaging and SDR demo

A small project for moving live data from Python to a browser through ActiveMQ. A Python publisher sends timestamps over STOMP; a Node.js/Express service consumes the messages and forwards them to the browser with Socket.IO. An optional RTL-SDR script computes signal spectra with NumPy and sends them through a separate queue.

This is an experiment in message flow and signal visualization. The included configuration is for a local development demo, with default broker credentials and ports exposed to the host. It is not a production deployment.

![ActiveMQ demo](img.png)

## Run the demo with Docker Compose

Install Docker with Compose, then clone this repository and open a terminal in its directory.

1. Copy the included environment template:

   ```bash
   cp .env.example .env
   ```

   In PowerShell, use `Copy-Item .env.example .env`.

2. Start the broker, web app, and timestamp publisher:

   ```bash
   docker compose up
   ```

   The entrypoint scripts install dependencies on startup. Leave `ACTIVEMQ_HOST=activemq` in `.env` for these containerized services.

3. Open [the web app](http://localhost:3000), [the latest messages view](http://localhost:3000/latest-view), or [the JSON endpoint](http://localhost:3000/latest). The timestamp publisher sends a message every second; SDR data appears only when the optional SDR script is running.

Stop the services with Ctrl+C, then `docker compose down`. The [ActiveMQ console](http://localhost:8161/admin) uses the local demo login `admin` / `admin`.

## Run the app and Python scripts locally

The repository's `versions.json` records Node.js 24 and Python 3.10. Use a fresh Python virtual environment; generated environments are not included in source control.

Start just the broker:

```bash
docker compose up -d activemq
```

Set `ACTIVEMQ_HOST=localhost` in `.env` when the app and Python scripts run on your host. Change it back to `activemq` before starting the app or publisher through Compose.

Install dependencies:

```bash
npm ci
python -m venv .venv
```

Activate the environment with `.venv\Scripts\Activate.ps1` in PowerShell, or `source .venv/bin/activate` on macOS/Linux, then install the Python dependencies:

```bash
python -m pip install -r requirements.txt
```

Run the app and publisher in separate terminals:

```bash
node --env-file=.env app.js
```

```bash
python publisher.py
```

The Python scripts load `.env` through `python-dotenv`. `npm start` also runs the app, but uses your shell's environment and the code's defaults; it does not load `.env` automatically.

## Optional RTL-SDR input

With the broker and app running, use the activated Python environment:

```bash
python test_activemq_connection.py
python sdr.py
```

Physical reception requires an RTL-SDR device, the appropriate USB driver, and the native RTL-SDR library available to Python. The script is configured for 162.450 MHz; adjust the settings in `sdr.py` for your device and signal.

For simulated data without the RTL-SDR Python package, use a separate virtual environment with only the runtime dependencies:

```bash
python -m pip install numpy stomp.py python-dotenv
python sdr.py
```

When `rtlsdr` cannot be imported, the script generates simulated samples. Do not rely on automatic fallback when the package is installed but the device cannot initialize; that path currently exits. `Dockerfile.sdr` is experimental and references an entrypoint that is not included, so the instructions here run SDR on the host.

## Project layout

| File | Purpose |
| --- | --- |
| `app.js` | Express routes, STOMP subscriptions, and Socket.IO events |
| `publisher.py` | Timestamp messages for the publisher queue |
| `sdr.py` | SDR samples, FFT processing, and spectrum messages |
| `creds.py` | Environment-based Python connection settings |
| `public/` | Browser interface and styles |
| `docker-compose.yml` | Broker, web app, and publisher services |
| `tests/` | Existing JavaScript and Python tests |

## Tests and linting

After installing dependencies, run:

```bash
npm test
python -m pytest
npm run lint:js
python -m pylint creds.py publisher.py sdr.py test_activemq_connection.py
```

The `test:py` and `lint:py` npm scripts assume a Windows virtual environment at `.venv\Scripts\python`. The direct Python commands above work with an activated environment on any platform. See [TESTING.md](TESTING.md) and [LINTING.md](LINTING.md) for more detail.

The GitHub Actions workflow currently reads `versions.json`; its lint and test jobs are commented out. Run checks locally rather than treating a green workflow as evidence that tests passed.

The current Python suite has known SDR test failures; see [the verification notes](TESTING.md#verification-notes). The JavaScript tests cover configuration and mocked Socket.IO behavior, not a live broker connection.

## Runtime versions

`versions.json` is read by GitHub Actions. Docker Compose reads `NODE_VERSION` and `PYTHON_VERSION` from `.env`, with its own defaults when those variables are absent. If you change runtime versions, update `versions.json` and your `.env` values together; there is no version-sync script in this repository.
