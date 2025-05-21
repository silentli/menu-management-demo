# Menu Management System

A Django-based menu ordering service with PostgreSQL integration, packaged with Docker for easy deployment.

## Features

- **Menu Management**: Create, update, and manage menu items
- **Inventory Tracking**: Real-time stock monitoring
- **Order Processing**: Streamlined order creation and management
- **Dual Interface**: Separate views for customers and staff
- **Docker Support**: Containerized deployment for consistency
- **Nginx Integration**: Production-grade web server with SSL support and optimized request handling

## Prerequisites

- Docker and Docker Compose
- Git
- Python 3.12 or later
- PostgreSQL client tools

## Environment Setup

Environment variables are managed using `.env` files located in `menu_management/settings/env/`.

- For production: `menu_management/settings/env/.env`
- For testing: `menu_management/settings/env/.env.test`
- Example template: `menu_management/settings/env/.env.example`

## Quick Start

```bash
# Clone the repository
git clone https://github.com/silentli/menu-management-demo.git
cd menu-management-demo

# Build and start all containers
docker compose -f docker/docker-compose.yml up --build -d

# Access the application
http://localhost/menu/  # Customer menu interface
http://localhost/staff/ # Staff management interface
```

## Architecture

The application uses a multi-container setup:
- **Web**: Django application server
- **Nginx**: Web server for handling HTTP requests and serving static files
- **PostgreSQL**: Database server

## Code Quality

### Linting

The project uses `ruff` for linting and code quality checks. To run the linter:

```bash
# Install linting dependencies
pip install -r requirements/quality.txt

# Run the linter
ruff check .

# Run the linter with auto-fix
ruff check --fix .
```

Common linting rules:
- `RUF022`: `__all__` lists must be sorted alphabetically
- `E501`: Line length should not exceed 88 characters
- `F401`: Unused imports should be removed

### Pre-commit Hooks

The project includes pre-commit hooks to ensure code quality before commits:

```bash
# Install pre-commit
pip install pre-commit

# Install the git hooks
pre-commit install

# Run pre-commit on all files
pre-commit run --all-files
```

## Testing

### Setup Test Environment

1. Start the test database:
```bash
docker compose -f docker/docker-compose.test.yml up -d db
```

2. Install test dependencies:
```bash
pip install -r requirements/test.txt
```

3. Run database migrations:
```bash
DJANGO_ENV=test python manage.py migrate
```

### Running Tests

Run tests using pytest with the correct environment:

```bash
# Run all tests with coverage report
DJANGO_ENV=test python -m pytest --cov=menu_management --cov-report=term-missing

# Run specific test file
DJANGO_ENV=test python -m pytest menu_app/tests/models/test_models.py
```

### Test Suite Coverage

The test suite includes:
- Model tests (menu items, inventory, orders)
- View tests (customer and staff interfaces)
- Integration tests (order flow, inventory updates)
