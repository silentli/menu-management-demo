import pytest
from app.managers.menu_manager import MenuManager

@pytest.fixture
def empty_menu_file(create_mock_file):
    return create_mock_file("empty_menu.json", [])

@pytest.fixture
def valid_menu_file(create_mock_file):
    valid_menu = [
        {"id": 201, "name": "Fried Rice", "category": "Main Course", "price": 8.0},
        {"id": 101, "name": "Dumpling", "category": "Appetizer", "price": 5.0},
        {"id": 102, "name": "Spring Roll", "category": "Appetizer", "price": 4.5},
    ]
    return create_mock_file("menu.json", valid_menu)

@pytest.fixture
def missing_attributes_menu_file(create_mock_file):
    missing_attributes_menu = [
        {"id": 201, "name": "Fried Rice", "category": "Main Course"},
        {"id": 101, "name": "Dumpling", "price": 5.0}
    ]
    return create_mock_file("missing_attributes_menu_file.json", missing_attributes_menu)


def test_load_menu(valid_menu_file):
    menu_manager = MenuManager(valid_menu_file)
    menu_manager.load_menu()
    menu_items = menu_manager.get_menu_items()
    assert len(menu_items) == 3
    assert [item.id for item in menu_items] == [101, 102, 201]


def test_load_empty_menu_file(empty_menu_file):
    menu_manager = MenuManager(empty_menu_file)
    menu_manager.load_menu()
    menu_items = menu_manager.get_menu_items()
    assert menu_items == []


def test_load_missing_attributes_menu(missing_attributes_menu_file):
    menu_manager = MenuManager(missing_attributes_menu_file)
    with pytest.raises(TypeError):
        menu_manager.load_menu()
