# Menu Management System

A Django-based menu ordering service with PostgreSQL integration, packaged with Docker for easy deployment.

## Features

- **Menu Management**: Create, update, and manage menu items
- **Inventory Tracking**: Real-time stock monitoring
- **Order Processing**: Streamlined order creation and management
- **Dual Interface**: Separate views for customers and staff
- **Docker Support**: Containerized deployment for consistency

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
http://localhost:8000
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
