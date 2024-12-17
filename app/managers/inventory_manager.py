from app.models.inventory_item import InventoryItem
from typing import List, Dict
import json

class InventoryManager:
    def __init__(self, inventory_file: str):
        self.inventory_file = inventory_file
        self._inventory_map: Dict[int, InventoryItem] = {}

    def load_inventory(self) -> None:
        """loads inventory data from json file and stores it in a map"""
        with open(self.inventory_file, "r") as file:
            raw_data = json.load(file)
        self._inventory_map = {item["id"]: InventoryItem(**item) for item in raw_data}

    def get_quantity(self, item_id: int) -> int:
        """returns the quantity of an item by id"""
        item = self._inventory_map.get(item_id)
        return item.quantity if item else 0

    def adjust_quantity(self, item_id: int, delta: int) -> bool:
        """adjusts the quantity of an item. Returns True if successful."""
        item = self._inventory_map.get(item_id)
        if not item or item.quantity + delta < 0:
            return False
        item.quantity += delta
        return True

    def check_availability_by_id(self, item_id: int, required_quantity: int) -> bool:
        item = self._inventory_map.get(item_id)
        return item and item.quantity >= required_quantity
