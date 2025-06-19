# ActiveMQ Test Project

![ActiveMQ Test Project](img.png)

This is a test project for working with ActiveMQ using Node.js and Python.

## Project Structure

- `app.js` - Main Express.js application
- `publisher.py` - Python script for publishing messages to ActiveMQ
- `public/` - Static files for the web interface
- `routes/` - Express.js route handlers

## Getting Started

### Prerequisites

- Node.js (version specified in versions.json)
- Python (version specified in versions.json)
- Docker and Docker Compose (for running ActiveMQ)

> Note: This project uses a centralized version management approach with versions.json as the single source of truth for language versions.

### Installation

1. Clone the repository
2. Create a .env file from the template:
   ```bash
   cp .env
   ```
   (Edit the .env file if you need to customize any settings)
3. Install JavaScript dependencies:
   ```bash
   npm install
   ```
4. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

Start the ActiveMQ container and the application:

```bash
docker-compose up
```

Or start just the application:

```bash
npm start
```

## Code Quality and Testing

This project uses linting tools to maintain code quality and testing frameworks to ensure reliability:

- **ESLint** for JavaScript linting
- **Pylint** for Python linting
- **Jest** for JavaScript testing
- **pytest** for Python testing

For more information about the linting setup, see [LINTING.md](LINTING.md).

For more information about the testing setup, see [TESTING.md](TESTING.md).

## Version Management

This project uses a centralized approach to manage language versions:

1. **versions.json**: The single source of truth for Node.js and Python versions
2. **Docker Compose**: Uses environment variables from .env file
3. **GitHub Actions**: Reads versions directly from versions.json

### Updating Versions

To update the versions used in the project:

1. Edit `versions.json` to update the version numbers
2. Run the update script to sync your `.env` file:
   ```bash
   npm run update-versions
   ```
3. Run `docker-compose down` followed by `docker-compose up` to apply the changes

The update script automatically updates your `.env` file with the versions from `versions.json`.

### Running Linters and Tests

```bash
# Run all linters
npm run lint

# Run only JavaScript linter
npm run lint:js

# Run only Python linter
npm run lint:py

# Fix JavaScript linting issues automatically
npm run lint:js:fix

# Run JavaScript tests
npm test

# Run JavaScript tests in watch mode
npm run test:watch

# Run Python tests
npm run test:py

# Run all tests (JavaScript and Python)
npm run test:all
```

### Automated Linting and Testing

This project uses GitHub Actions to automatically run linters and tests on pull requests and pushes to the main branch. The workflow configuration is in `.github/workflows/linting.yml` and includes:

- Running ESLint on JavaScript files
- Running Pylint on Python files
- Running Jest tests for JavaScript
- Running pytest tests for Python

## Accessing ActiveMQ

ActiveMQ is now fully exposed and can be accessed from outside Docker using various protocols:

### Web Console

Access the ActiveMQ web console at: http://localhost:8161/admin

Default credentials:
- Username: admin
- Password: admin

The web console allows you to:
- Monitor queues and topics
- View message counts and statistics
- Send test messages
- Configure broker settings

### Connecting with Client Applications

ActiveMQ supports multiple protocols, all of which are exposed:

| Protocol | Port | Use Case | Client Libraries |
|----------|------|----------|-----------------|
| STOMP    | 61613 | Simple text-based protocol | stomp.py (Python), stomp.js (JavaScript) |
| OpenWire | 61616 | Java clients | ActiveMQ, JMS |
| MQTT     | 1883 | IoT devices | Paho (Python, JavaScript) |
| AMQP     | 5672 | Advanced messaging | qpid, proton |

### Connection Examples

**Python (STOMP):**
```python
import stomp
conn = stomp.Connection(host_and_ports=[('localhost', 61613)])
conn.connect('admin', 'admin', wait=True)
conn.send(destination='/queue/test', body='Hello from Python!')
```

**JavaScript (STOMP):**
```javascript
const client = Stomp.client('ws://localhost:61613');
client.connect('admin', 'admin', () => {
  client.send('/queue/test', {}, 'Hello from JavaScript!');
});
```

**Java (OpenWire):**
```java
ActiveMQConnectionFactory factory = new ActiveMQConnectionFactory("tcp://localhost:61616");
Connection connection = factory.createConnection("admin", "admin");
// ... continue with JMS operations
```

### Accessing from Another Machine

To access ActiveMQ from another machine on your network, replace `localhost` with your computer's IP address in all connection strings.

## Using RTL-SDR

The project now supports two ways to run the RTL-SDR component:
1. **Locally on your host machine** (recommended for Windows users)
2. **In a Docker container** (better for Linux users)

### Running sdr.py Locally (Windows)

Running sdr.py directly on your Windows machine provides better USB device access and simplifies the setup:

1. **Run the setup script**:
   ```
   setup_local_sdr.bat
   ```
   This script will:
   - Create a Python virtual environment
   - Install required Python dependencies
   - Create a default .env file if needed
   - Provide instructions for RTL-SDR driver installation

2. **Install RTL-SDR drivers** (if using physical hardware):
   - Download Zadig from https://zadig.akeo.ie/
   - Plug in your RTL-SDR device
   - Run Zadig, select your RTL-SDR device, and install the WinUSB driver
   - Download the RTL-SDR software from https://www.rtl-sdr.com/downloads
   - Extract the files and add the bin directory to your PATH

3. **Start the ActiveMQ and other services**:
   ```
   docker-compose up -d
   ```

4. **Test the ActiveMQ connection**:
   ```
   .venv\Scripts\activate
   python test_activemq_connection.py
   ```
   This will verify that your local machine can connect to the ActiveMQ container.

   > **Important**: When running scripts locally, make sure your `.env` file has `ACTIVEMQ_HOST=localhost` (not "activemq"). The setup script creates this file correctly, but if you're having connection issues, check this setting.

5. **Run sdr.py**:
   ```
   python sdr.py
   ```

The script will automatically detect if an RTL-SDR device is available. If not, it will run in simulation mode.

### Running sdr.py in Docker (Linux)

For Linux users, running in Docker with USB passthrough is still an option:

1. **Modify docker-compose.yml**:
   Uncomment the sdr service section in docker-compose.yml if you want to run it in Docker.

2. **USB Device Access**:
   Linux supports direct USB device passthrough to Docker. The docker-compose.yml file is configured to pass through USB devices to the container.

3. **Start all services**:
   ```bash
   docker-compose up
   ```

### WSL2 Configuration (Windows with Docker)

If you prefer to use Docker on Windows with WSL2:

1. Connect your RTL-SDR device
2. In PowerShell (as Administrator), run:
   ```powershell
   usbipd list
   usbipd bind -b <BUSID>
   usbipd attach --wsl -b <BUSID>
   ```
3. Then in WSL2, verify the device is available with `lsusb`
4. Start the Docker containers with `docker-compose up`

### Simulation Mode

The sdr.py script includes a fallback simulation mode that activates automatically when:
- The pyrtlsdr module is not available
- An RTL-SDR device cannot be accessed

This allows the service to run and send simulated spectrum data to ActiveMQ even without physical hardware.

## License

This project is licensed under the MIT License.
