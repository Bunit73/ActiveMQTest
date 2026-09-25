# Testing Guide

This project has JavaScript and Python unit tests. Most messaging behavior is mocked, so passing unit tests does not verify a live ActiveMQ connection.

## Verification notes

During the documentation cleanup on September 25, 2026, the existing suites were run on Windows with Node.js 24.2.0 and Python 3.13.0:

- JavaScript: 4 tests passed across 2 suites.
- Python: 8 passed, 1 failed, and 3 errored. The SDR tests still patch a nonexistent `sdr.creds` attribute, and the simulated-sample test assumes a magnitude limit that conflicts with the generated signal peaks.
- `docker compose --env-file .env.example config --quiet` validated the Compose configuration. The Docker engine was not running, so the complete broker-to-browser flow and physical SDR hardware were not verified.

These are existing test limitations; the cleanup did not change application behavior. Run the commands below to check the current state in your environment.

## JavaScript Testing with Jest

Jest is configured to test the JavaScript components of the application, including the Express server and Socket.io functionality.

### Running JavaScript Tests

To run the JavaScript tests:

```bash
npm test
```

To run the tests in watch mode (useful during development):

```bash
npm run test:watch
```

### Jest Configuration

The Jest configuration is stored in `jest.config.js` in the project root. Key features include:

- Node.js test environment
- Tests located in the `tests/js` directory with `.test.js` extension
- Code coverage reporting
- Exclusion of node_modules, coverage reports, and test files from coverage

### JavaScript Test Structure

The JavaScript tests are organized as follows:

- `tests/js/app.test.js`: Tests for environment variable handling in app.js
- `tests/js/socket.test.js`: Tests for Socket.io integration and STOMP client functionality

## Python Testing with pytest

pytest is configured to test the Python components of the application, including the publisher script and credentials handling.

### Running Python Tests

To run the Python tests:

```bash
npm run test:py
```

Or you can run it directly with the Python interpreter from the virtual environment:

```bash
.venv\Scripts\python -m pytest
```

If you have activated the virtual environment, you can simply use:

```bash
pytest
```

### pytest Configuration

The pytest configuration is stored in `pytest.ini` in the project root. Key features include:

- Tests located in the `tests/python` directory with `test_*.py` naming pattern
- Verbose output
- Code coverage reporting

### Python Test Structure

The Python tests are organized as follows:

- `tests/python/test_publisher.py`: Tests for the publisher script
- `tests/python/test_creds.py`: Tests for the credentials module
- `tests/python/conftest.py`: Shared fixtures for Python tests

## Running All Tests

To run both JavaScript and Python tests at once:

```bash
npm run test:all
```

## Automated Testing with GitHub Actions

The workflow in `.github/workflows/linting.yml` is triggered by pushes and pull requests to `main` and `master`. Currently only its version-reading job is active; the ESLint, Pylint, Jest, and pytest jobs are commented out. Run tests locally to verify a change.

## Installation

The testing tools are included as development dependencies in the project. After cloning the repository:

1. Install JavaScript dependencies:
   ```bash
   npm install
   ```

2. Install Python dependencies in a virtual environment:
   ```bash
   # Create and activate a virtual environment
   python -m venv .venv
   .venv\Scripts\activate  # On Windows
   # source .venv/bin/activate  # On macOS/Linux

   # Install dependencies including pytest
   pip install -r requirements.txt
   ```

## Writing Tests

### JavaScript Tests

When writing JavaScript tests:

1. Create a new file in the `tests/js` directory with a `.test.js` extension
2. Use Jest's `describe` and `test` functions to structure your tests
3. Use Jest's mocking capabilities to mock dependencies
4. Run the tests with `npm test`

Example:

```javascript
// tests/js/example.test.js
describe('Example Test', () => {
  test('should pass', () => {
    expect(true).toBe(true);
  });
});
```

### Python Tests

When writing Python tests:

1. Create a new file in the `tests/python` directory with a `test_*.py` naming pattern
2. Use pytest's fixtures for setup and teardown
3. Use pytest-mock for mocking dependencies
4. Run the tests with `npm run test:py`

Example:

```python
# tests/python/test_example.py
def test_example():
    assert True
```

## Code Coverage

Both Jest and pytest are configured to generate code coverage reports. After running the tests, you can view the coverage reports:

- JavaScript: Open `coverage/lcov-report/index.html` in a browser
- Python: Open `htmlcov/index.html` in a browser

The coverage reports show which lines of code are covered by tests and which are not, helping you identify areas that need more testing.
