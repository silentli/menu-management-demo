import os
import time
from decimal import Decimal

import pytest
from django.conf import settings
from django.test import Client

from menu_app.models.inventory import InventoryItem
from menu_app.models.menu_item import MenuItem
from menu_app.models.order import Order


def is_postgres_ready():
    """Check if PostgreSQL is ready to accept connections."""
    try:
        # Get port from environment or use default
        port = os.environ.get('POSTGRES_PORT', '5433')

        # Check if we're in CI environment
        if os.getenv('CI'):
            # In CI, PostgreSQL is running directly
            os.system(f'pg_isready -h localhost -p {port} > /dev/null 2>&1')
        else:
            # In local environment, use docker-compose
            os.system(
                f'docker compose -f docker/docker-compose.test.yml '
                f'exec -T db pg_isready -h localhost -p {port} > /dev/null 2>&1'
            )
        return True
    except Exception:
        return False


def wait_for_postgres(max_retries=30, delay=1):
    """Wait for PostgreSQL to be ready."""
    for i in range(max_retries):
        if is_postgres_ready():
            return True
        time.sleep(delay)
    return False


@pytest.fixture(scope='session')
def django_db_setup():
    """Configure test database settings."""
    # Wait for PostgreSQL to be ready
    if not wait_for_postgres():
        raise Exception('PostgreSQL is not ready after maximum retries')

    # Print database settings for debugging
    print('\nDjango Database Settings:')
    print('----------------------')
    print(f"NAME: {settings.DATABASES['default']['NAME']}")
    print(f"USER: {settings.DATABASES['default']['USER']}")
    print(f"HOST: {settings.DATABASES['default']['HOST']}")
    print(f"PORT: {settings.DATABASES['default']['PORT']}")
    print('------------------------------')


@pytest.fixture
def client():
    """A Django test client instance."""
    return Client()


@pytest.fixture
def test_data():
    """Fixture providing test data for menu items."""
    return {
        'name': 'Test Item',
        'category': 'main',
        'price': Decimal('10.99'),
        'quantity': 5,
    }


@pytest.fixture
def menu_item(test_data):
    """Fixture providing a test menu item."""
    return MenuItem.objects.create(
        name=test_data['name'], category=test_data['category'], price=test_data['price']
    )


@pytest.fixture
def inventory_item(menu_item, test_data):
    """Fixture providing a test inventory item."""
    return InventoryItem.objects.create(menu_item=menu_item, quantity=test_data['quantity'])


@pytest.fixture
def order(menu_item):
    """Fixture providing a test order."""
    return Order.objects.create(status='pending')


@pytest.fixture
def order_item(order, menu_item):
    """Create a test order item."""
    return order.items.create(
        menu_item=menu_item, quantity=1, price_at_time_of_order=menu_item.price
    )
