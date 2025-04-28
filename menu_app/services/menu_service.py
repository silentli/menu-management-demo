import logging
from typing import List, Optional, Dict
from django.db import transaction

from menu_app.models import menu_item
from menu_app.services import menu_utils

logger = logging.getLogger(__name__)


def get_menu_item_by_id(menu_item_id: int) -> Optional[menu_item.MenuItem]:
    """
    Get a menu item by ID
    """
    return menu_utils.get_menu_item(menu_item_id=menu_item_id)


def get_menu_item_by_name(name: str) -> Optional[menu_item.MenuItem]:
    """
    Get a menu item by name
    """
    return menu_utils.get_menu_item(name=name)


def get_menu_items_by_ids(menu_item_ids: List[int]) -> Dict[int, menu_item.MenuItem]:
    """
    Get multiple menu items by IDs with validation.
    
    Args:
        menu_item_ids: List of menu item IDs
        
    Returns:
        Dictionary mapping IDs to menu items
        
    Raises:
        ValueError: If the input is invalid
    """
    if not menu_item_ids:
        raise ValueError("Menu item IDs list cannot be empty")
        
    result = menu_utils.get_menu_items_bulk(menu_item_ids=menu_item_ids)
    if len(result) != len(menu_item_ids):
        missing_ids = set(menu_item_ids) - set(result.keys())
        logger.warning(f"Some menu items not found: {missing_ids}")
    return result


def get_menu_items_by_names(names: List[str]) -> Dict[str, menu_item.MenuItem]:
    """
    Get multiple menu items by names with validation.
    
    Args:
        names: List of menu item names
        
    Returns:
        Dictionary mapping names to menu items
        
    Raises:
        ValueError: If the input is invalid
    """
    if not names:
        raise ValueError("Menu item names list cannot be empty")
        
    standardized_names = list(map(str.strip, names))
    result = menu_utils.get_menu_items_bulk(names=standardized_names)
    if len(result) != len(standardized_names):
        missing_names = set(standardized_names) - set(result.keys())
        logger.warning(f"Some menu items not found: {missing_names}")
    return result


def get_full_menu() -> List[menu_item.MenuItem]:
    """
    Get the complete menu with all items
    """
    return menu_utils.get_all_menu_items()


def get_category_menu(category: str) -> List[menu_item.MenuItem]:
    """
    Get all menu items in a specific category with standardized category name.
    
    Args:
        category: The category to filter by
        
    Returns:
        List of menu items in the specified category
        
    Raises:
        ValueError: If the category is invalid
    """
    if not category or not category.strip():
        raise ValueError("Category cannot be empty")
        
    standardized_category = category.strip().lower()
    return menu_utils.get_menu_items_by_category(standardized_category)


def get_current_menu() -> List[menu_item.MenuItem]:
    """
    Get the current menu with only available items
    """
    return menu_utils.get_available_menu_items()


def search_menu(query: str) -> List[menu_item.MenuItem]:
    """
    Search the menu by name or category with standardized query.
    
    Args:
        query: The search query
        
    Returns:
        List of matching menu items
        
    Raises:
        ValueError: If the query is invalid
    """
    if not query or not query.strip():
        raise ValueError("Search query cannot be empty")
        
    return menu_utils.search_menu_items(query.strip())


def find_menu_item(name: str, cutoff: float = 0.6) -> Optional[menu_item.MenuItem]:
    """
    Find a menu item by name with fuzzy matching and standardized input.
    
    Args:
        name: The name to search for
        cutoff: The similarity threshold for fuzzy matching (0.0 to 1.0)
        
    Returns:
        The matching menu item or None if not found
        
    Raises:
        ValueError: If the parameters are invalid
    """
    if not name or not name.strip():
        raise ValueError("Menu item name cannot be empty")
    if not 0.0 <= cutoff <= 1.0:
        raise ValueError("Cutoff must be between 0.0 and 1.0")
        
    return menu_utils.find_menu_item_by_name(name.strip(), use_fuzzy=True, cutoff=cutoff)


@transaction.atomic
def is_item_available(menu_item: menu_item.MenuItem, quantity: int = 1) -> bool:
    """
    Check if a menu item is available in the requested quantity with transaction support.
    
    Args:
        menu_item: The menu item to check
        quantity: The quantity to check availability for
        
    Returns:
        bool: True if the item is available in the requested quantity
        
    Raises:
        ValueError: If the quantity is invalid
        RuntimeError: If there are issues checking inventory
    """
    if quantity <= 0:
        raise ValueError("Quantity must be positive")
        
    try:
        return menu_utils.check_item_availability(menu_item, quantity)
    except Exception as e:
        logger.error(f"Error checking availability for {menu_item.name}: {str(e)}")
        raise RuntimeError(f"Failed to check item availability: {str(e)}")


@transaction.atomic
def add_menu_item(
    name: str,
    description: str,
    price: float,
    category: str,
    image_url: str = None
) -> menu_item.MenuItem:
    """
    Add a new item to the menu with validation and transaction support.
    
    Args:
        name: Name of the menu item
        description: Description of the menu item
        price: Price of the menu item (must be positive)
        category: Category of the menu item
        image_url: Optional URL for the menu item image
        
    Returns:
        The created menu item
        
    Raises:
        ValueError: If the menu item data is invalid
        RuntimeError: If there are issues creating the menu item
    """
    # Validate input
    if not name or not name.strip():
        raise ValueError("Menu item name cannot be empty")
    if price <= 0:
        raise ValueError("Menu item price must be positive")
    if not category or not category.strip():
        raise ValueError("Menu item category cannot be empty")
        
    try:
        return menu_utils.create_menu_item(
            name=name.strip(),
            description=description.strip() if description else "",
            price=price,
            category=category.strip().lower(),
            image_url=image_url
        )
    except Exception as e:
        logger.error(f"Error creating menu item {name}: {str(e)}")
        raise RuntimeError(f"Failed to create menu item: {str(e)}")


@transaction.atomic
def modify_menu_item(
    menu_item: menu_item.MenuItem,
    name: str = None,
    price: float = None,
    category: str = None,
    sold_out: bool = None
) -> menu_item.MenuItem:
    """
    Modify an existing menu item with validation and transaction support.
    
    Args:
        menu_item: The menu item to modify
        name: New name for the menu item
        price: New price for the menu item (must be positive)
        category: New category for the menu item
        sold_out: New sold out status for the menu item
        
    Returns:
        The updated menu item
        
    Raises:
        ValueError: If the menu item data is invalid
        RuntimeError: If there are issues updating the menu item
    """
    # Validate input
    if name is not None and not name.strip():
        raise ValueError("Menu item name cannot be empty")
    if price is not None and price <= 0:
        raise ValueError("Menu item price must be positive")
    if category is not None and not category.strip():
        raise ValueError("Menu item category cannot be empty")
        
    # Prepare update data
    update_data = {}
    if name is not None:
        update_data['name'] = name.strip()
    if price is not None:
        update_data['price'] = price
    if category is not None:
        update_data['category'] = category.strip().lower()
    if sold_out is not None:
        update_data['sold_out'] = sold_out
        
    if not update_data:
        raise ValueError("No fields to update")
        
    try:
        return menu_utils.update_menu_item(menu_item, **update_data)
    except Exception as e:
        logger.error(f"Error updating menu item {menu_item.name}: {str(e)}")
        raise RuntimeError(f"Failed to update menu item: {str(e)}")
