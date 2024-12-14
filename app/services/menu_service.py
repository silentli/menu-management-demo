from app.managers.menu_manager import MenuManager
from app.managers.inventory_manager import InventoryManager

class MenuService:
    def __init__(self, menu_manager: MenuManager, inventory_manager: InventoryManager):
        self.menu_manager = menu_manager
        self.inventory_manager = inventory_manager

    def prepare_menu(self) -> list[dict]:
        """prepares menu data with inventory details"""
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

    def display_menu(self) -> None:
        """displays the menu grouped by category"""
        from itertools import groupby
        grouped_menu = groupby(self.menu_manager.get_menu_items(), key=lambda x: x.category)
        for category, items in grouped_menu:
            print(f"\n=== Category: {category} ===")
            for item in items:
                quantity = self.inventory_manager.get_quantity(item.id)
                sold_out_label = " (Sold Out)" if quantity == 0 else ""
                print(f"  {item.name} - ${item.price:.2f}{sold_out_label}")
