# TCP Echo Server

A modern Python TCP Echo Server implementation that listens on port 8989 by default.

## Features

- Asynchronous TCP server using `asyncio`
- Type-annotated code with strict mypy checking
- Comprehensive test suite
- Modern Python project structure
- Proper logging

## Requirements

- Python 3.11 or higher

## Installation

1. Clone the repository
2. Install the package in development mode:
```bash
pip install -e ".[dev]"
```

## Usage

Run the server:
```bash
python -m echo_server
```

The server will start listening on port 8989 by default. You can test it using netcat:
```bash
nc localhost 8989
```

Type any message and press enter - the server will echo it back.

## Development

### Running Tests

```bash
pytest
```

### Code Quality

The project uses several tools to ensure code quality:

- Black for code formatting:
```bash
black echo_server tests
```

- Ruff for linting:
```bash
ruff check .
```

- Mypy for type checking:
```bash
mypy echo_server tests
```

## License

MIT 