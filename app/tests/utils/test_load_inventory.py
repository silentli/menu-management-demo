import pytest
import json
from app.utils.load_inventory import load_inventory
from app.models.inventory_item import InventoryItem

@pytest.fixture
def inventory_data():
    return [
        {"id": 101, "quantity": 30},
        {"id": 102, "quantity": 15},
    ]

# creat a mock inventory file
@pytest.fixture
def mock_inventory_file(tmp_path, inventory_data):
    inventory_path = tmp_path / "inventory.json"
    inventory_path.write_text(json.dumps(inventory_data))
    return str(inventory_path)

# Test case using both fixtures
def test_load_inventory(mock_inventory_file, inventory_data):
    inventory = load_inventory(mock_inventory_file)
    assert inventory == [InventoryItem(**item) for item in inventory_data]
