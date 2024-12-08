from app.models.order_item import OrderItem
from app.models.menu_item import MenuItem

def test_order_item_initialization():
    menu_item = MenuItem(name="Dumpling", price=5.0, category="Appetizer")
    order_item = OrderItem(menu_item=menu_item, quantity=2)
    assert order_item.menu_item == menu_item
    assert order_item.quantity == 2