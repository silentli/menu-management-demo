import json
from typing import List
from app.models.inventory_item import InventoryItem

# load inventory json file and convert to InventoryItem
def load_inventory(file_path: str) -> List[InventoryItem]:
    with open(file_path, "r") as file:
        raw_data = json.load(file)
    return [InventoryItem(**item) for item in raw_data]
