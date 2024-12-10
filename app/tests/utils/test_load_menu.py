import pytest
import json
from app.utils.load_menu import load_menu
from app.models.menu_item import MenuItem

@pytest.fixture
def menu_data():
    return [
        {"id": 101, "category": "Appetizer", "name": "Dumpling", "price": 5.0},
        {"id": 102, "category": "Appetizer", "name": "Spring Roll", "price": 4.5},
    ]

# create a mock json file
@pytest.fixture
def mock_menu_file(tmp_path, menu_data):
    menu_path = tmp_path / "menu.json"
    menu_path.write_text(json.dumps(menu_data))
    return str(menu_path)

def test_load_menu(mock_menu_file, menu_data):
    menu = load_menu(mock_menu_file)
    assert menu == [MenuItem(**item) for item in menu_data]
