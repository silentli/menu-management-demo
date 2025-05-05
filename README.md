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
- PostgreSQL (for local development)

## Quick Start

### Docker Deployment (Recommended)

```bash
# Clone the repository
git clone https://github.com/silentli/menu-management-demo.git
cd menu-management-demo

# Start the application
docker-compose up -d

# Access the application
http://localhost:8000
```

## Local Development

1. **Environment Setup**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Database Configuration**
   ```bash
   createdb menu_management
   python manage.py migrate
   ```

3. **Run Development Server**
   ```bash
   python manage.py runserver
   ```

## Configuration

### Database Settings
Default PostgreSQL configuration:
- Database: menu_management
- User: postgres
- Password: postgres
- Host: localhost (or 'db' in Docker)
- Port: 5432

### Environment Variables
Override default settings using:
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST`
- `DB_PORT`

## Architecture

- **Backend**: Django Framework
- **Database**: PostgreSQL
- **Containerization**: Docker
- **Frontend**: Bootstrap
- **Deployment**: Microservice-ready
