from dataclasses import dataclass
from app.models.menu_item import MenuItem

@dataclass
class OrderItem:
    menu_item: MenuItem
    quantity: int
