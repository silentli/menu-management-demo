"""
Utility functions for menu-specific operations.
"""
import logging
from typing import Dict, List, Optional

from django.db.models import Q

from menu_app.models import menu_item, inventory
from menu_app.services import db_utils

logger = logging.getLogger(__name__)


def get_menu_item(menu_item_id: int = None, name: str = None) -> Optional[menu_item.MenuItem]:
    """
    Get menu item by ID or name.
    Exactly one of menu_item_id or name must be provided.
    """
    return db_utils.get_model_instance(menu_item.MenuItem, id=menu_item_id, name=name)


def get_menu_items_bulk(menu_item_ids: List[int] = None, names: List[str] = None) -> Dict:
    """
    Get multiple menu items by IDs or names in one query.
    Exactly one of menu_item_ids or names must be provided.
    """
    return db_utils.get_model_instances_bulk(menu_item.MenuItem, ids=menu_item_ids, names=names)


def get_all_menu_items() -> List[menu_item.MenuItem]:
    """
    Get all menu items ordered by category and name
    """
    return list(db_utils.get_model_queryset(menu_item.MenuItem).order_by('category', 'name'))


def get_menu_items_by_category(category: str) -> List[menu_item.MenuItem]:
    """
    Get menu items filtered by category
    """
    return list(db_utils.get_model_queryset(menu_item.MenuItem, category=category).order_by('name'))


def get_available_menu_items() -> List[menu_item.MenuItem]:
    """
    Get menu items that are not sold out and have inventory
    """
    return list(db_utils.get_model_queryset(
        menu_item.MenuItem,
        sold_out=False,
        inventory__quantity__gt=0
    ).order_by('category', 'name'))


def find_menu_item_by_name(
    name: str,
    use_fuzzy: bool = False,
    cutoff: float = 0.6
) -> Optional[menu_item.MenuItem]:
    """
    Find a menu item by name with optional fuzzy matching

    Args:
        name: Name to search for
        use_fuzzy: Whether to use fuzzy matching (default: False)
        cutoff: Similarity threshold for fuzzy matching
    """
    # Try exact match first
    exact_match = get_menu_item(name=name)
    if exact_match:
        return exact_match
        
    if not use_fuzzy:
        return None

    # Try partial match
    partial_match = db_utils.get_model_queryset(
        menu_item.MenuItem,
        name__icontains=name
    ).first()
    if partial_match:
        return partial_match

    # Try fuzzy match only if enabled
    # ruff: noqa: E402
    from difflib import get_close_matches
    menu_item_names = list(
        db_utils.get_model_queryset(menu_item.MenuItem)
        .values_list('name', flat=True)
    )
    close_matches = get_close_matches(name, menu_item_names, n=1, cutoff=cutoff)

    if not close_matches:
        logger.warning(f"No menu item matching '{name}' found")
        return None

    closest_name = close_matches[0]
    return get_menu_item(name=closest_name)


def search_menu_items(query: str) -> List[menu_item.MenuItem]:
    """
    Search menu items by name or category
    """
    return list(db_utils.get_model_queryset(menu_item.MenuItem).filter(
        Q(name__icontains=query) | Q(category__icontains=query)
    ).order_by('category', 'name'))


def check_item_availability(menu_item: menu_item.MenuItem, quantity: int = 1) -> bool:
    """
    Check if the requested quantity of a menu item is available
    """
    if menu_item.sold_out:
        return False

    try:
        inventory_item = inventory.InventoryItem.objects.get(menu_item=menu_item)
        return inventory_item.quantity >= quantity
    except inventory.InventoryItem.DoesNotExist:
        logger.warning(f"No inventory found for menu item {menu_item.name}")
        return False


def create_menu_item(
    name: str,
    description: str,
    price: float,
    category: str,
    image_url: str = None
) -> menu_item.MenuItem:
    """
    Create a new menu item
    """
    return db_utils.create_model_instance(
        menu_item.MenuItem,
        name=name,
        description=description,
        price=price,
        category=category,
        image_url=image_url
    )


def update_menu_item(
    menu_item: menu_item.MenuItem,
    name: str = None,
    price: float = None,
    category: str = None,
    sold_out: bool = None
) -> menu_item.MenuItem:
    """
    Update an existing menu item
    """
    update_data = {}
    if name is not None:
        update_data['name'] = name
    if price is not None:
        update_data['price'] = price
    if category is not None:
        update_data['category'] = category
    if sold_out is not None:
        update_data['sold_out'] = sold_out

    return db_utils.update_model_instance(menu_item, **update_data)
