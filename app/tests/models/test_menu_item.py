from app.models.menu_item import MenuItem

def test_menu_item_initialization():
    item = MenuItem(name="Dumpling", price=5.0, category="Appetizer")
    assert item.name == "Dumpling"
    assert item.price == 5.0
    assert item.category == "Appetizer"

def test_menu_item_equality():
    item1 = MenuItem(name="Dumpling", price=5.0, category="Appetizer")
    item2 = MenuItem(name="Dumpling", price=5.0, category="Appetizer")
    assert item1 == item2

def test_menu_item_different():
    item1 = MenuItem(name="Dumpling", price=5.0, category="Appetizer")
    item2 = MenuItem(name="Tea", price=2.0, category="Beverage")
    assert item1 != item2