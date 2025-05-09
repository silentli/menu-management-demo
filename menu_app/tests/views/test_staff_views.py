import pytest
from django.urls import reverse
from django.test import override_settings
from django.contrib.auth.models import User
from django.conf import settings
from menu_app.services import inventory_service
from menu_app.models.order import Order

# Test password for staff authentication
TEST_STAFF_PASSWORD = 'test_staff_password'  # Must match the value in conftest.py

@pytest.fixture
def staff_user():
    """Fixture providing a staff user."""
    user, created = User.objects.get_or_create(
        username='staff',
        defaults={
            'is_staff': True,
            'is_active': True
        }
    )
    # Set the password to match settings.STAFF_PASSWORD
    user.set_password(settings.STAFF_PASSWORD)
    user.save()
    return user

@pytest.fixture
def staff_data():
    """Fixture providing staff-specific test data."""
    return {
        'username': 'staff',
        'password': TEST_STAFF_PASSWORD,
        'is_staff': True
    }

@pytest.mark.django_db
def test_staff_login_success(client, staff_user):
    """Test successful staff login."""
    response = client.post(reverse('menu_app:staff_login'), {
        'password': settings.STAFF_PASSWORD
    })
    assert response.status_code == 302  # Redirect after successful login
    assert client.session.get('_auth_user_id') == str(staff_user.id)

@pytest.mark.django_db
def test_staff_login_failure(client):
    """Test failed staff login."""
    response = client.post(reverse('menu_app:staff_login'), {
        'password': 'wrong_password'
    })
    assert response.status_code == 200  # Stay on login page
    assert '_auth_user_id' not in client.session

@pytest.mark.django_db
def test_staff_dashboard_view(client, staff_user):
    """Test staff dashboard access."""
    # Test without login
    response = client.get(reverse('menu_app:staff_dashboard'))
    assert response.status_code == 302  # Redirect to login

    # Test with login
    client.login(username='staff', password=settings.STAFF_PASSWORD)
    response = client.get(reverse('menu_app:staff_dashboard'))
    assert response.status_code == 200
    assert 'orders' in response.context

@pytest.mark.django_db
def test_order_management_view(client, staff_user, menu_item, order):
    """Test order management functionality."""
    client.login(username='staff', password=settings.STAFF_PASSWORD)
    
    # Test order list view
    response = client.get(reverse('menu_app:staff_order_list'))
    assert response.status_code == 200
    assert str(order.id) in response.content.decode()
    
    # Test completing an order
    response = client.post(reverse('menu_app:staff_order_detail', args=[order.id]), {
        'action': 'complete'
    })
    assert response.status_code == 302  # Redirect after completion
    order.refresh_from_db()
    assert order.status == 'completed'
    
    # Test canceling an order
    new_order = Order.objects.create(status="pending")
    response = client.post(reverse('menu_app:staff_order_detail', args=[new_order.id]), {
        'action': 'cancel'
    })
    assert response.status_code == 302  # Redirect after cancellation
    new_order.refresh_from_db()
    assert new_order.status == 'cancelled'

@pytest.mark.django_db
def test_inventory_management_view(client, staff_user, menu_item, inventory_item):
    """Test inventory management functionality."""
    client.login(username='staff', password=settings.STAFF_PASSWORD)
    
    # Test inventory list view
    response = client.get(reverse('menu_app:inventory_list'))
    assert response.status_code == 200
    assert str(menu_item.name) in response.content.decode()
    
    # Test updating inventory
    initial_quantity = inventory_item.quantity
    target_quantity = 50
    
    response = client.post(reverse('menu_app:inventory_update', args=[menu_item.id]), {
        'quantity': target_quantity
    })
    assert response.status_code == 302  # Redirect after update
    
    # Force a fresh database query to get the latest state
    updated_inventory = inventory_service.get_inventory(menu_item)
    assert updated_inventory is not None
    assert updated_inventory.quantity == target_quantity 