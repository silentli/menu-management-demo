from app.models.menu_item import MenuItem
import json

class MenuManager:
    def __init__(self, menu_file: str):
        self.menu_file = menu_file
        self._menu_items: list[MenuItem] = []

    def load_menu(self) -> None:
        """loads menu data from json file and sorts it by id"""
        with open(self.menu_file, "r") as file:
            raw_data = json.load(file)
        self._menu_items = sorted(
            [MenuItem(**item) for item in raw_data],
            key=lambda item: item.id
        )

    def get_menu_items(self) -> list[MenuItem]:
        """returns all loaded menu items."""
        return self._menu_items
