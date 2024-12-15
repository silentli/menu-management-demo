from itertools import groupby
from app.managers.menu_manager import MenuManager
from app.managers.inventory_manager import InventoryManager

class MenuService:
    def __init__(self, menu_manager: MenuManager, inventory_manager: InventoryManager):
        self.menu_manager = menu_manager
        self.inventory_manager = inventory_manager

    def prepare_menu(self) -> list[dict]:
        """prepares menu data with sold_out details for api or other responses"""
        menu_output = []
        for item in self.menu_manager.get_menu_items():
            quantity = self.inventory_manager.get_quantity(item.id)
            menu_output.append({
                "id": item.id,
                "name": item.name,
                "category": item.category,
                "price": item.price,
                "sold_out": quantity == 0,
            })
        return menu_output

    def format_menu(self) -> str:
        """formats the menu grouped by category for display"""
        formatted_output = []
        grouped_menu = groupby(self.menu_manager.get_menu_items(), key=lambda x: x.category)
        for category, items in grouped_menu:
            formatted_output.append(f"\n=== {category} ===")
            for item in items:
                quantity = self.inventory_manager.get_quantity(item.id)
                sold_out_label = " (Sold Out)" if quantity == 0 else ""
                formatted_output.append(f"  {item.name} - ${item.price:.2f}{sold_out_label}")
        return "\n".join(formatted_output)

    def display_menu(self) -> None:
        print(self.format_menu())
