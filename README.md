# ActiveMQ Test Project

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

## License

This project is licensed under the MIT License.
