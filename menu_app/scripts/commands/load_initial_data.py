import json
import os
from django.core.management.base import BaseCommand
from menu_app.models import MenuItem, InventoryItem

class Command(BaseCommand):
    help = 'Load initial menu items and inventory data from JSON file'

    def handle(self, *args, **options):
        # Get the path to the JSON file
        data_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            'data',
            'initial_menu_items.json'
        )

        try:
            # Read the JSON file
            with open(data_file, 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'Data file not found: {data_file}'))
            return
        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR(f'Invalid JSON in file: {data_file}'))
            return

        # Create menu items if none exist
        if not MenuItem.objects.exists():
            for item_data in data['menu_items']:
                try:
                    menu_item = MenuItem.objects.create(
                        category=item_data['category'],
                        name=item_data['name'],
                        price=item_data['price']
                    )
                    # Create inventory for each menu item
                    InventoryItem.objects.create(
                        menu_item=menu_item,
                        quantity=data['initial_inventory_quantity']
                    )
                    self.stdout.write(self.style.SUCCESS(f'Created menu item: {item_data["name"]}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error creating menu item {item_data["name"]}: {str(e)}'))
            
            self.stdout.write(self.style.SUCCESS('Successfully loaded initial data'))
        else:
            self.stdout.write(self.style.WARNING('Menu items already exist, skipping data load')) 