import pytest
from app.managers.inventory_manager import InventoryManager

@pytest.fixture
def inventory_data():
    return [
        {"id": 101, "quantity": 10},
        {"id": 102, "quantity": 0},
        {"id": 201, "quantity": 25},
    ]

@pytest.fixture
def valid_inventory_file(create_mock_file, inventory_data):
    return create_mock_file("inventory.json", inventory_data)

@pytest.fixture
def empty_inventory_file(create_mock_file):
    return create_mock_file("empty_inventory.json", [])

@pytest.fixture
def missing_attributes_inventory_file(create_mock_file):
    missing_attributes_inventory = [
        {"id": 101},
        {"quantity": 10},
    ]
    return create_mock_file("missing_attributes_inventory_file.json", missing_attributes_inventory)

def test_load_inventory(valid_inventory_file, inventory_data):
    inventory_manager = InventoryManager(valid_inventory_file)
    inventory_manager.load_inventory()
    for item in inventory_data:
        assert inventory_manager.get_quantity(item["id"]) == item["quantity"]

def test_load_empty_inventory(empty_inventory_file):
    inventory_manager = InventoryManager(empty_inventory_file)
    inventory_manager.load_inventory()

    assert inventory_manager.get_quantity(101) == 0

def test_load_missing_attributes_inventory(missing_attributes_inventory_file):
    inventory_manager = InventoryManager(missing_attributes_inventory_file)
    with pytest.raises(TypeError):
        inventory_manager.load_inventory()
