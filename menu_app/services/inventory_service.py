import logging
from typing import Dict, List, Optional

from django.db import transaction

from menu_app.models.menu_item import MenuItem
from menu_app.models.inventory import InventoryItem

logger = logging.getLogger(__name__)


def get_menu_item(menu_item_id: int = None, name: str = None) -> Optional[MenuItem]:
    """
    Get menu item by ID or name.
    Exactly one of menu_item_id or name must be provided.

    menu_item_id: ID of the menu item
    name: Name of the menu item
    """
    if menu_item_id is not None and name is not None:
        raise ValueError("Only one of menu_item_id or name should be provided")
    if menu_item_id is None and name is None:
        raise ValueError("Either menu_item_id or name must be provided")
        
    try:
        if menu_item_id is not None:
            return MenuItem.objects.get(id=menu_item_id)
        return MenuItem.objects.get(name=name)
    except MenuItem.DoesNotExist:
        logger.warning(f"Menu item not found (id={menu_item_id}, name={name})")
        return None


def get_menu_items_bulk(menu_item_ids: List[int] = None, names: List[str] = None) -> Dict:
    """
    Get multiple menu items by IDs or names in one query.
    Exactly one of menu_item_ids or names must be provided.
    
    menu_item_ids: List of menu item IDs
    names: List of menu item names
    """
    if menu_item_ids is not None and names is not None:
        raise ValueError("Only one of menu_item_ids or names should be provided")
    if menu_item_ids is None and names is None:
        raise ValueError("Either menu_item_ids or names must be provided")
        
    if menu_item_ids is not None:
        return MenuItem.objects.in_bulk(menu_item_ids)
    return {item.name: item for item in MenuItem.objects.filter(name__in=names)}


def _get_base_inventory_queryset():
    """
    Returns the base queryset for inventory items with menu items pre-selected.
    This is used internally by other functions to avoid repeating the select_related.
    """
    return InventoryItem.objects.select_related('menu_item')


def get_inventory(menu_item: MenuItem) -> Optional[InventoryItem]:
    """
    Get inventory for a menu item.
    
    menu_item: The MenuItem to get inventory for
    """
    try:
        return _get_base_inventory_queryset().get(menu_item=menu_item)
    except InventoryItem.DoesNotExist:
        logger.warning(f"No inventory found for menu item {menu_item.name}")
        return None


def get_all_inventory_items():
    """
    Get all inventory items with their associated menu items.
    
    Returns:
        QuerySet of all InventoryItems with menu items pre-selected
    """
    return _get_base_inventory_queryset().all()


def get_low_stock_items(threshold: int = 5):
    """
    Get inventory items with stock below the specified threshold.
    
    Args:
        threshold: Minimum quantity threshold
        
    Returns:
        QuerySet of low stock InventoryItems
    """
    return _get_base_inventory_queryset().filter(
        quantity__lt=threshold
    ).order_by('quantity')


def check_availability(menu_item: MenuItem, quantity: int) -> bool:
    """
    Check if the requested quantity of a menu item is available.
    
    menu_item: The MenuItem to check
    quantity: Quantity to check availability for
    """
    if menu_item.sold_out:
        return False
        
    inventory = get_inventory(menu_item)
    return inventory.quantity >= quantity if inventory else False


@transaction.atomic
def update_inventory(menu_item: MenuItem, quantity_change: int) -> bool:
    """
    Update inventory for a menu item.
    
    menu_item: The MenuItem to update inventory for
    quantity_change: Amount to change inventory by (positive to add, negative to subtract)
    """
    try:
        inventory = _get_base_inventory_queryset().select_for_update().get(menu_item=menu_item)
        
        new_quantity = inventory.quantity + quantity_change
        if new_quantity < 0:
            logger.warning(f"Cannot reduce inventory below 0 for {menu_item.name}")
            return False
            
        inventory.quantity = new_quantity
        inventory.save()
        
        # Update sold_out status if needed
        if new_quantity == 0 and not menu_item.sold_out:
            menu_item.sold_out = True
            menu_item.save()
        elif new_quantity > 0 and menu_item.sold_out:
            menu_item.sold_out = False
            menu_item.save()
            
        logger.info(f"Updated inventory for {menu_item.name}: {inventory.quantity} (+{quantity_change if quantity_change > 0 else quantity_change})")
        return True
        
    except InventoryItem.DoesNotExist:
        # Create new inventory if it doesn't exist (only for positive quantity changes)
        if quantity_change <= 0:
            logger.warning(f"Cannot decrease non-existent inventory for {menu_item.name}")
            return False
            
        InventoryItem.objects.create(menu_item=menu_item, quantity=quantity_change)
        
        # Update sold_out status
        if menu_item.sold_out:
            menu_item.sold_out = False
            menu_item.save()
            
        logger.info(f"Created inventory for {menu_item.name}: {quantity_change}")
        return True


@transaction.atomic
def bulk_update_inventory(updates: Dict[int, int]) -> Dict[int, bool]:
    """
    Update inventory for multiple menu items at once.
    
    Args:
        updates: Dict mapping menu_item_id to quantity_change
        
    Returns:
        Dict mapping menu_item_id to success/failure
    """
    # Get all menu items in one query
    menu_items = get_menu_items_bulk(menu_item_ids=list(updates.keys()))
    
    results = {}
    for menu_item_id, quantity_change in updates.items():
        menu_item = menu_items.get(menu_item_id)
        if not menu_item:
            results[menu_item_id] = False
            continue
            
        results[menu_item_id] = update_inventory(menu_item, quantity_change)
            
    return results
