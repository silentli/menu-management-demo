import pytest
from decimal import Decimal
from django.core.exceptions import ValidationError
from menu_app.models.menu_item import MenuItem
from menu_app.models.inventory import InventoryItem
from menu_app.models.order import Order, OrderItem

def assert_menu_item(menu_item, test_data):
    """Helper function to assert menu item properties."""
    assert menu_item.name == test_data['name']
    assert menu_item.category == test_data['category']
    assert menu_item.price == test_data['price']

def assert_inventory_item(inventory_item, test_data):
    """Helper function to assert inventory item properties."""
    assert inventory_item.quantity == test_data['quantity']
    if 'low_stock_threshold' in test_data:
        assert inventory_item.low_stock_threshold == test_data['low_stock_threshold']

@pytest.mark.django_db
def test_menu_item_creation(menu_item, test_data):
    assert_menu_item(menu_item, test_data)

@pytest.mark.django_db
def test_inventory_item_creation(inventory_item, test_data):
    assert_inventory_item(inventory_item, test_data)

@pytest.mark.django_db
def test_order_creation(order, menu_item):
    """Test order creation and status management."""
    assert order.status == 'pending'
    
    # Test order item creation
    order_item = OrderItem.objects.create(
        order=order,
        menu_item=menu_item,
        quantity=1,
        price_at_time_of_order=menu_item.price
    )
    assert order_item.quantity == 1
    assert order_item.price_at_time_of_order == menu_item.price
