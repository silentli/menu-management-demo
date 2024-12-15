import pytest
from unittest.mock import Mock
from app.services.menu_service import MenuService
from app.models.menu_item import MenuItem

@pytest.fixture
def mock_menu_manager():
    menu_manager = Mock()
    menu_manager.get_menu_items.return_value = [
        MenuItem(id=101, name="Dumpling", category="Appetizer", price=5.0),
        MenuItem(id=102, name="Spring Roll", category="Appetizer", price=4.5),
        MenuItem(id=201, name="Fried Rice", category="Main Course", price=8.0),
        MenuItem(id=301, name="Tea", category="Beverage", price=2.0),
    ]
    return menu_manager

@pytest.fixture
def mock_inventory_manager():
    inventory_manager = Mock()
    inventory_manager.get_quantity.side_effect = lambda item_id: {
        101: 10,
        102: 0,
        201: 5,
        301: 0
    }.get(item_id, 0)
    return inventory_manager

@pytest.fixture
def menu_service(mock_menu_manager, mock_inventory_manager):
    return MenuService(menu_manager=mock_menu_manager, inventory_manager=mock_inventory_manager)


def test_prepare_menu(menu_service):
    prepared_menu = menu_service.prepare_menu()

    expected_output = [
        {"id": 101, "name": "Dumpling", "category": "Appetizer", "price": 5.0, "sold_out": False},
        {"id": 102, "name": "Spring Roll", "category": "Appetizer", "price": 4.5, "sold_out": True},
        {"id": 201, "name": "Fried Rice", "category": "Main Course", "price": 8.0, "sold_out": False},
        {"id": 301, "name": "Tea", "category": "Beverage", "price": 2.0, "sold_out": True},
    ]
    assert prepared_menu == expected_output

def test_format_menu(menu_service):
    """test key elements of the formatted menu"""
    formatted_menu = menu_service.format_menu()

    assert "Dumpling - $5.00" in formatted_menu
    assert "Spring Roll - $4.50 (Sold Out)" in formatted_menu
    assert "Tea - $2.00 (Sold Out)" in formatted_menu
