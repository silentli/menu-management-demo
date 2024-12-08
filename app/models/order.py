from dataclasses import dataclass, field

from app.models.menu_item import MenuItem
from app.models.order_item import OrderItem

@dataclass
class Order:
    id: int
    order_items: list[OrderItem] = field(default_factory=list)

    @property
    def total_price(self)-> float:
        # calculate the total price of the order
        return sum(order_item.menu_item.price * order_item.quantity for order_item in self.order_items)

    def _find_order_item(self, menu_item: MenuItem) -> OrderItem | None:
        return next((order_item for order_item in self.order_items if order_item.menu_item == menu_item), None)

    def add_item(self, menu_item: MenuItem, quantity: int = 1) -> None:
        existing_order_item = self._find_order_item(menu_item)
        if existing_order_item:
            existing_order_item.quantity += quantity
        else:
            self.order_items.append(OrderItem(menu_item=menu_item, quantity=quantity))

    def remove_item(self, menu_item: MenuItem, quantity: int = 1) -> None:
        existing_order_item = self._find_order_item(menu_item)
        if not existing_order_item:
            raise ValueError(f"Item {menu_item.name} not found in order.")

        if existing_order_item.quantity > quantity:
            existing_order_item.quantity -= quantity
        else:
            self.order_items.remove(existing_order_item)