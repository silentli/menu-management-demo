from app.models.menu_item import MenuItem

def test_menu_item_initialization():
    item = MenuItem(id=101, category="Appetizer", name="Dumpling", price=5.0)
    assert item.id == 101
    assert item.category == "Appetizer"
    assert item.name == "Dumpling"
    assert item.price == 5.0

def test_menu_item_equality():
    item1 = MenuItem(id=101, category="Appetizer", name="Dumpling", price=5.0)
    item2 = MenuItem(id=101, category="Appetizer", name="Dumpling", price=5.0)
    assert item1 == item2

def test_menu_item_different():
    item1 = MenuItem(id=101, category="Appetizer", name="Dumpling", price=5.0)
    item2 = MenuItem(id=301, category="Beverage", name="Tea", price=2.0)
    assert item1 != item2