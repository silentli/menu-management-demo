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

Run tests using pytest:

```bash
# Run all tests
python -m pytest

# Run with verbose output
python -m pytest -v

# Run specific test file
python -m pytest menu_app/tests/models/test_models.py
```

The test suite includes:
- Model tests (menu items, inventory, orders)
- View tests (customer and staff interfaces)
- Integration tests (order flow, inventory updates)
