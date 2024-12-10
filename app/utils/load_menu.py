import json
from ..models.menu_item import MenuItem

# load menu json file and convert to MenuItem
def load_menu(menu_path: str) -> list[MenuItem]:
    with open(menu_path, "r") as file:
        raw_data = json.load(file)
    return [MenuItem(**item) for item in raw_data]
