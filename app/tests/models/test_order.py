import pytest
from app.models.menu_item import MenuItem
from app.models.order import Order
from app.models.order_item import OrderItem

@pytest.fixture
def dumpling():
    return MenuItem(id=101, category="Appetizer", name="Dumpling", price=5.0)

@pytest.fixture
def fried_rice():
    return MenuItem(id=201, category="Main Course", name="Fried Rice", price=8.0)

@pytest.fixture
def tea():
    return MenuItem(id=301, category="Beverage", name="Tea", price=2.0)

def test_order_initialization(dumpling, tea):
    order_item_1 = OrderItem(menu_item=dumpling, quantity=2)
    order_item_2 = OrderItem(menu_item=tea, quantity=3)

    order = Order(id=1, order_items=[order_item_1, order_item_2])

    assert order.id == 1
    assert len(order.order_items) == 2
    assert order.total_price == 16.0


def test_add_new_item(dumpling, tea):
    order = Order(id=1, order_items=[OrderItem(menu_item=dumpling, quantity=2)])
    order.add_item(menu_item=tea, quantity=2)

    assert len(order.order_items) == 2
    assert order.total_price == 14.0


def test_add_existing_item(dumpling):
    order = Order(id=1, order_items=[OrderItem(menu_item=dumpling, quantity=2)])
    order.add_item(menu_item=dumpling, quantity=3)

    assert len(order.order_items) == 1
    assert order.order_items[0].quantity == 5
    assert order.total_price == 25.0


def test_remove_partial_quantity(dumpling):
    order = Order(id=1, order_items=[OrderItem(menu_item=dumpling, quantity=3)])
    order.remove_item(menu_item=dumpling, quantity=1)

    assert len(order.order_items) == 1
    assert order.order_items[0].quantity == 2
    assert order.total_price == 10.0


def test_remove_full_quantity(dumpling):
    order = Order(id=1, order_items=[OrderItem(menu_item=dumpling, quantity=2)])
    order.remove_item(menu_item=dumpling, quantity=2)

    assert len(order.order_items) == 0
    assert order.total_price == 0.0


def test_remove_item_not_in_order(dumpling, fried_rice):
    order = Order(id=1, order_items=[OrderItem(menu_item=dumpling, quantity=2)])

    with pytest.raises(ValueError, match="Item Fried Rice not found in order"):
        order.remove_item(menu_item=fried_rice, quantity=1)


def test_total_price_with_multiple_items(dumpling, tea, fried_rice):
    order = Order(
        id=1,
        order_items=[
            OrderItem(menu_item=dumpling, quantity=2),
            OrderItem(menu_item=tea, quantity=3),
            OrderItem(menu_item=fried_rice, quantity=1),
        ]
    )

    assert len(order.order_items) == 3
    assert order.total_price == 24.0
