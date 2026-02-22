# hass-external-conversation-agent

This is a Python project using `uv` for dependency management.

## Project Structure

- `main.py` - Main entry point
- `log.py` - Logging utilities (debug, info, warn, error functions)
- `pyproject.toml` - Project metadata and dependencies
- `uv.lock` - Locked dependency versions
- `Makefile` - Development commands
- `.env` - Environment variables (not committed to git)

## Adding Dependencies

To add a new package:
```bash
make install <package-name>
```

This will:
1. Add the package to `pyproject.toml`
2. Update `uv.lock` with resolved versions
3. Install the package in the virtual environment

## Running the Project

```bash
make start
```

This automatically:
- Loads environment variables from `.env` if present
- Runs the project in the virtual environment

## Environment Variables

Add environment variables to `.env`:
```
DATABASE_URL=postgres://localhost/mydb
API_KEY=your-api-key-here
```

These are automatically loaded when running `make start`.

## Available Commands

- `make init` - Initialize project (first time setup)
- `make install` - Install all dependencies
- `make install <package>` - Add a new package
- `make start` - Run the project

## Python Version

This project requires Python 3.13 or higher (see `pyproject.toml`).
