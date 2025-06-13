# Linting Guide

This project uses linting tools to maintain code quality and consistency for both JavaScript and Python code.

## JavaScript Linting with ESLint

ESLint is configured to enforce a standard coding style based on the popular "Standard" style guide with some custom modifications.

### Running JavaScript Linting

To check your JavaScript code for style and potential issues:

```bash
npm run lint:js
```

To automatically fix many common JavaScript linting issues:

```bash
npm run lint:js:fix
```

### ESLint Configuration

The ESLint configuration is stored in `.eslintrc.js` in the project root. Key features include:

- Based on the Standard style guide
- Enforces semicolons (unlike the default Standard style)
- Warns about unused variables instead of throwing errors
- Configured for both browser and Node.js environments
- Ignores `node_modules` and vendor JavaScript files

## Python Linting with Pylint

Pylint is configured to enforce Python code quality and style.

### Running Python Linting

To check your Python code for style and potential issues:

```bash
npm run lint:py
```

Or you can run it directly with the Python interpreter from the virtual environment:

```bash
.venv\Scripts\python -m pylint *.py
```

If you have activated the virtual environment, you can simply use:

```bash
pylint *.py
```

### Pylint Configuration

The Pylint configuration is stored in `.pylintrc` in the project root. Key features include:

- Maximum line length of 100 characters
- 4-space indentation
- Disabled some overly strict warnings (like missing docstrings)
- Reasonable limits for code complexity metrics

## Running All Linters

To run both JavaScript and Python linters at once:

```bash
npm run lint
```

## Automated Linting with GitHub Actions

This project uses GitHub Actions to automatically run linters on pull requests and pushes to the main branch. This ensures that all code changes maintain the project's code quality standards.

The workflow configuration is in `.github/workflows/linting.yml` and includes:

- Running ESLint on JavaScript files
- Running Pylint on Python files

The workflow runs on:
- Pushes to the main and master branches
- Pull requests to the main and master branches

This automated process helps catch linting issues early in the development process.

## Installation

The linting tools are included as development dependencies in the project. After cloning the repository:

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

   # Install dependencies including Pylint
   pip install -r requirements.txt
   ```

## Integrating with Your Editor

Many code editors support ESLint and Pylint integration for real-time linting:

- **VS Code**: Install the ESLint and Pylint extensions
- **WebStorm/PyCharm**: Built-in support for ESLint and Pylint
- **Sublime Text**: Install SublimeLinter with ESLint and Pylint plugins
- **Atom**: Install linter-eslint and linter-pylint packages

## Customizing Linting Rules

If you need to modify the linting rules:

- For JavaScript: Edit `.eslintrc.js`
- For Python: Edit `.pylintrc`
