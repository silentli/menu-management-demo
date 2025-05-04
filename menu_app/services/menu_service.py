import logging
from typing import List, Optional, Dict, Union
from django.db import transaction
from functools import wraps

from menu_app.models import menu_item
from menu_app.services import menu_utils

logger = logging.getLogger(__name__)

def validate_category(category: str) -> str:
    """Validate and standardize category name"""
    if not category or not category.strip():
        raise ValueError("Category cannot be empty")
    
    standardized_category = category.strip().lower()
    valid_categories = [choice[0] for choice in menu_item.MenuItem.CATEGORY_CHOICES]
    if standardized_category not in valid_categories:
        raise ValueError(f"Invalid category. Must be one of: {', '.join(valid_categories)}")
    return standardized_category

def validate_name(name: str) -> str:
    """Validate and standardize menu item name"""
    if not name or not name.strip():
        raise ValueError("Name cannot be empty")
    return name.strip()

def validate_price(price: float) -> float:
    """Validate price"""
    if price <= 0:
        raise ValueError("Price must be positive")
    return price

def with_transaction(func):
    """Decorator to handle transactions and logging"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            with transaction.atomic():
                result = func(*args, **kwargs)
                logger.info(f"Successfully executed {func.__name__}")
                return result
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            raise
    return wrapper

def get_menu_item(**kwargs) -> Optional[menu_item.MenuItem]:
    """
    Get a menu item by ID or name
    """
    return menu_utils.get_menu_item(**kwargs)

def get_menu_items(**kwargs) -> Dict[Union[int, str], menu_item.MenuItem]:
    """
    Get multiple menu items by IDs or names with validation
    """
    if not kwargs:
        raise ValueError("Must provide either menu_item_ids or names")
        
    if 'menu_item_ids' in kwargs:
        ids = kwargs['menu_item_ids']
        if not ids:
            raise ValueError("Menu item IDs list cannot be empty")
        result = menu_utils.get_menu_items_bulk(menu_item_ids=ids)
        if len(result) != len(ids):
            missing = set(ids) - set(result.keys())
            logger.warning(f"Some menu items not found: {missing}")
    else:
        names = kwargs['names']
        if not names:
            raise ValueError("Menu item names list cannot be empty")
        standardized_names = list(map(str.strip, names))
        result = menu_utils.get_menu_items_bulk(names=standardized_names)
        if len(result) != len(standardized_names):
            missing = set(standardized_names) - set(result.keys())
            logger.warning(f"Some menu items not found: {missing}")
    return result

def get_menu(category: Optional[str] = None, available_only: bool = False) -> List[menu_item.MenuItem]:
    """
    Get menu items with optional filtering
    """
    if category:
        standardized_category = validate_category(category)
        return menu_utils.get_menu_items_by_category(standardized_category)
    elif available_only:
        return menu_utils.get_available_menu_items()
    else:
        return menu_utils.get_all_menu_items()

def search_menu(query: str) -> List[menu_item.MenuItem]:
    """
    Search the menu by name or category
    """
    if not query or not query.strip():
        raise ValueError("Search query cannot be empty")
    return menu_utils.search_menu_items(query.strip())

@with_transaction
def is_item_available(menu_item: menu_item.MenuItem, quantity: int = 1) -> bool:
    """
    Check if a menu item is available in the requested quantity
    """
    if quantity <= 0:
        raise ValueError("Quantity must be positive")
    return menu_utils.check_item_availability(menu_item, quantity)

@with_transaction
def add_menu_item(name: str, price: float, category: str) -> menu_item.MenuItem:
    """
    Add a new menu item
    """
    standardized_name = validate_name(name)
    validated_price = validate_price(price)
    validated_category = validate_category(category)
    
    # Check for existing item
    if menu_utils.get_menu_item(name=standardized_name):
        raise ValueError(f"Menu item with name '{standardized_name}' already exists")
    
    # Create new menu item
    new_item = menu_item.MenuItem(
        name=standardized_name,
        price=validated_price,
        category=validated_category
    )
    new_item.save()
    return new_item

@with_transaction
def modify_menu_item(
    menu_item: menu_item.MenuItem,
    name: Optional[str] = None,
    price: Optional[float] = None,
    category: Optional[str] = None
) -> menu_item.MenuItem:
    """
    Modify an existing menu item
    """
    if not menu_item:
        raise ValueError("Menu item cannot be None")
    
    if name is not None:
        standardized_name = validate_name(name)
        if standardized_name != menu_item.name:
            if menu_utils.get_menu_item(name=standardized_name):
                raise ValueError(f"Menu item with name '{standardized_name}' already exists")
            menu_item.name = standardized_name
    
    if price is not None:
        menu_item.price = validate_price(price)
    
    if category is not None:
        menu_item.category = validate_category(category)
    
    menu_item.save()
    return menu_item
