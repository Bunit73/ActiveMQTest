# ActiveMQ Test Project

This is a test project for working with ActiveMQ using Node.js and Python.

## Project Structure

- `app.js` - Main Express.js application
- `publisher.py` - Python script for publishing messages to ActiveMQ
- `public/` - Static files for the web interface
- `routes/` - Express.js route handlers

## Getting Started

### Prerequisites

- Node.js (v14 or higher)
- Python (v3.6 or higher)
- Docker and Docker Compose (for running ActiveMQ)

### Installation

1. Clone the repository
2. Install JavaScript dependencies:
   ```bash
   npm install
   ```
3. Install Python dependencies:
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

## Code Quality

This project uses linting tools to maintain code quality:

- **ESLint** for JavaScript
- **Pylint** for Python

For more information about the linting setup, see [LINTING.md](LINTING.md).

### Running Linters

```bash
# Run all linters
npm run lint

# Run only JavaScript linter
npm run lint:js

# Run only Python linter
npm run lint:py

# Fix JavaScript linting issues automatically
npm run lint:js:fix
```

### Automated Linting

This project uses GitHub Actions to automatically run linters on pull requests and pushes to the main branch. The workflow configuration is in `.github/workflows/linting.yml`.

## License

This project is licensed under the MIT License.
