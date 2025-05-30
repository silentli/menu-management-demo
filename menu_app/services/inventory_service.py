import logging
from typing import Dict, List, Optional

from django.db import transaction

from menu_app.models import inventory, menu_item
from menu_app.services import db_utils, menu_utils

logger = logging.getLogger(__name__)


def _get_base_inventory_queryset():
    """
    Returns the base queryset for inventory items with menu items pre-selected.
    to avoid repeating the select_related
    """
    return db_utils.get_model_queryset(inventory.InventoryItem).select_related('menu_item')


@transaction.atomic
def create_inventory(
    menu_item: menu_item.MenuItem,
    initial_quantity: int = 0,
    low_stock_threshold: int = 5,
) -> inventory.InventoryItem:
    """
    Create a new inventory item for a menu item.

    Args:
        menu_item: The MenuItem to create inventory for
        initial_quantity: Initial quantity (default: 0)
        low_stock_threshold: Threshold for low stock warning (default: 5)

    Returns:
        The created InventoryItem

    Raises:
        ValueError: If menu_item is invalid, inventory already exists,
                   or initial_quantity/low_stock_threshold are invalid
    """
    if not menu_item:
        raise ValueError('Menu item cannot be None')

    if not menu_item.id:
        raise ValueError('Menu item must be saved before creating inventory')

    if get_inventory(menu_item):
        raise ValueError(f'Inventory already exists for menu item {menu_item.name}')

    try:
        # Create inventory item with validation
        inventory_item = inventory.InventoryItem(
            menu_item=menu_item,
            quantity=0,  # Start with 0 and use add_stock for proper validation
            low_stock_threshold=low_stock_threshold,
        )
        inventory_item.save()

        # Use the model's add_stock method if initial quantity is provided
        if initial_quantity > 0:
            inventory_item.add_stock(initial_quantity)

        return inventory_item
    except Exception as e:
        logger.error(f'Error creating inventory for {menu_item.name}: {e!s}')
        raise RuntimeError(f'Failed to create inventory: {e!s}')


def get_inventory(menu_item: menu_item.MenuItem) -> Optional[inventory.InventoryItem]:
    """
    Get inventory for a menu item.

    Args:
        menu_item: The MenuItem to get inventory for

    Returns:
        InventoryItem or None if not found
    """
    try:
        return _get_base_inventory_queryset().get(menu_item=menu_item)
    except inventory.InventoryItem.DoesNotExist:
        logger.warning(f'No inventory found for menu item {menu_item.name}')
        return None


def get_all_inventory_items() -> List[inventory.InventoryItem]:
    """
    Get all inventory items with their related menu items
    """
    return list(_get_base_inventory_queryset().all())


def get_inventory_by_menu_item(
    menu_item: menu_item.MenuItem,
) -> Optional[inventory.InventoryItem]:
    """
    Get inventory for a specific menu item
    """
    return get_inventory(menu_item)


def get_inventory_by_menu_item_name(name: str) -> Optional[inventory.InventoryItem]:
    """
    Get inventory for a menu item by its name

    Args:
        name: Name of the menu item

    Returns:
        InventoryItem or None if not found

    Raises:
        ValueError: If the name is invalid
    """
    if not name or not name.strip():
        raise ValueError('Menu item name cannot be empty')

    menu_item = menu_utils.get_menu_item(name=name.strip())
    if not menu_item:
        logger.warning(f"No menu item found with name '{name}'")
        return None
    return get_inventory(menu_item)


def get_low_stock_items(threshold: int = 10) -> List[inventory.InventoryItem]:
    """
    Get inventory items with quantity below threshold

    Args:
        threshold: Minimum quantity threshold

    Returns:
        List of inventory items below threshold

    Raises:
        ValueError: If threshold is not positive
    """
    if threshold <= 0:
        raise ValueError('Threshold must be positive')
    return list(_get_base_inventory_queryset().filter(quantity__lt=threshold))


@transaction.atomic
def add_stock(menu_item: menu_item.MenuItem, quantity: int) -> None:
    """
    Add stock to a menu item's inventory

    Args:
        menu_item: The MenuItem to add stock to
        quantity: Amount of stock to add

    Raises:
        ValueError: If quantity is not positive
        RuntimeError: If there are issues adding stock
    """
    if quantity <= 0:
        raise ValueError('Quantity must be positive')

    try:
        inventory_item = get_inventory(menu_item)
        if not inventory_item:
            inventory_item = create_inventory(menu_item, initial_quantity=0)
        inventory_item.quantity += quantity
        db_utils.update_model_instance(inventory_item, quantity=inventory_item.quantity)
    except Exception as e:
        logger.error(f'Error adding stock to {menu_item.name}: {e!s}')
        raise RuntimeError(f'Failed to add stock: {e!s}')


@transaction.atomic
def remove_stock(menu_item: menu_item.MenuItem, quantity: int) -> None:
    """
    Remove stock from a menu item's inventory

    Args:
        menu_item: The MenuItem to remove stock from
        quantity: Amount of stock to remove

    Raises:
        ValueError: If quantity is not positive or insufficient stock
        RuntimeError: If there are issues removing stock
    """
    if quantity <= 0:
        raise ValueError('Quantity must be positive')

    if not menu_utils.check_item_availability(menu_item, quantity):
        raise ValueError(f'Insufficient stock for {menu_item.name}')

    try:
        inventory_item = get_inventory(menu_item)
        if not inventory_item:
            raise ValueError(f'No inventory found for menu item {menu_item.name}')

        inventory_item.quantity -= quantity
        db_utils.update_model_instance(inventory_item, quantity=inventory_item.quantity)
    except Exception as e:
        logger.error(f'Error removing stock from {menu_item.name}: {e!s}')
        raise RuntimeError(f'Failed to remove stock: {e!s}')


def check_availability(menu_item: menu_item.MenuItem, quantity: int) -> bool:
    """
    Check if the requested quantity of a menu item is available.

    Args:
        menu_item: The MenuItem to check
        quantity: Quantity to check availability for

    Returns:
        True if available, False otherwise

    Raises:
        ValueError: If quantity is not positive
    """
    if quantity <= 0:
        raise ValueError('Quantity must be positive')
    return menu_utils.check_item_availability(menu_item, quantity)


@transaction.atomic
def update_inventory(menu_item: menu_item.MenuItem, quantity_change: int) -> None:
    """
    Update inventory for a menu item by adding or removing stock.
    This is a convenience function that uses add_stock or remove_stock internally.

    Args:
        menu_item: The MenuItem to update inventory for
        quantity_change: Amount to change inventory by
            (positive to add, negative to subtract)

    Raises:
        ValueError: If quantity_change is zero
        RuntimeError: If there are issues updating inventory
    """
    logger.debug(f'Updating inventory for {menu_item.name}: quantity_change={quantity_change}')

    if quantity_change == 0:
        raise ValueError('Quantity change cannot be zero')

    try:
        if quantity_change > 0:
            add_stock(menu_item, quantity_change)
        else:
            remove_stock(menu_item, abs(quantity_change))
    except Exception as e:
        logger.error(f'Error updating inventory for {menu_item.name}: {e!s}')
        raise RuntimeError(f'Failed to update inventory: {e!s}')


@transaction.atomic
def bulk_update_inventory(updates: Dict[int, int]) -> Dict[int, bool]:
    """
    Update inventory for multiple menu items at once.

    Args:
        updates: Dict mapping menu_item_id to quantity_change

    Returns:
        Dict mapping menu_item_id to success/failure

    Raises:
        ValueError: If updates dictionary is empty
    """
    if not updates:
        raise ValueError('Updates dictionary cannot be empty')

    # Get all menu items in one query
    menu_items = menu_utils.get_menu_items_bulk(menu_item_ids=list(updates.keys()))

    results = {}
    for menu_item_id, quantity_change in updates.items():
        menu_item = menu_items.get(menu_item_id)
        if not menu_item:
            logger.warning(f'Menu item {menu_item_id} not found')
            results[menu_item_id] = False
            continue

        try:
            update_inventory(menu_item, quantity_change)
            results[menu_item_id] = True
        except Exception as e:
            logger.error(f'Error updating inventory for menu item {menu_item_id}: {e!s}')
            results[menu_item_id] = False

    return results
