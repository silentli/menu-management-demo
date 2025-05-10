"""
Order service for handling order-related operations.
This module manages orders and their items.
"""

import logging
from typing import List, Optional

from django.db import transaction

from menu_app.models import menu_item, order
from menu_app.services import db_utils, inventory_service, menu_utils

logger = logging.getLogger(__name__)


def _get_base_order_queryset():
    """
    Returns the base queryset for orders with items pre-selected
    to avoid repeating the select_related
    """
    return db_utils.get_model_queryset(order.Order).prefetch_related('items', 'items__menu_item')


def get_order(order_id: str) -> Optional[order.Order]:
    """
    Get an order by ID

    Raises:
        ValueError: If order_id is invalid
    """
    if not order_id:
        raise ValueError('Order ID cannot be empty')

    try:
        return _get_base_order_queryset().get(id=order_id)
    except order.Order.DoesNotExist:
        logger.warning(f'Order {order_id} not found')
        return None


def get_all_orders() -> List[order.Order]:
    """
    Get all orders with their items
    """
    return list(_get_base_order_queryset().all())


@transaction.atomic
def create_order() -> order.Order:
    """
    Create a new empty order
    """
    try:
        return db_utils.create_model_instance(order.Order)
    except Exception as e:
        logger.error(f'Error creating order: {e!s}')
        raise RuntimeError(f'Failed to create order: {e!s}')


@transaction.atomic
def add_item_to_order(order_id: str, menu_item_id: int, quantity: int = 1) -> None:
    """
    Add an item to an order and reduce inventory

    Args:
        order_id: The ID of the order
        menu_item_id: The ID of the menu item to add
        quantity: The quantity to add (default: 1)

    Raises:
        ValueError: If parameters are invalid or order/menu item not found
        RuntimeError: If there are issues adding the item
    """
    if quantity <= 0:
        raise ValueError('Quantity must be positive')

    try:
        order_obj = get_order(order_id)
        if not order_obj:
            raise ValueError(f'Order {order_id} not found')

        menu_item_obj = menu_utils.get_menu_item(menu_item_id=menu_item_id)
        if not menu_item_obj:
            raise ValueError(f'Menu item {menu_item_id} not found')

        # Check if item already exists in order
        existing_item = order_obj.find_order_item(menu_item_obj)
        if existing_item:
            # Check if we have enough inventory for the additional quantity
            if not menu_utils.check_item_availability(menu_item_obj, quantity):
                raise ValueError(f'Insufficient stock for {menu_item_obj.name}')
            existing_item.quantity += quantity
            db_utils.update_model_instance(existing_item, quantity=existing_item.quantity)
            # Reduce inventory for the additional quantity
            inventory_service.remove_stock(menu_item_obj, quantity)
        else:
            # Check if we have enough inventory for the new item
            if not menu_utils.check_item_availability(menu_item_obj, quantity):
                raise ValueError(f'Insufficient stock for {menu_item_obj.name}')
            # Create the order item
            db_utils.create_model_instance(
                order.OrderItem,
                order=order_obj,
                menu_item=menu_item_obj,
                quantity=quantity,
            )
            # Reduce inventory
            inventory_service.remove_stock(menu_item_obj, quantity)
    except Exception as e:
        logger.error(f'Error adding item to order {order_id}: {e!s}')
        raise RuntimeError(f'Failed to add item to order: {e!s}')


@transaction.atomic
def remove_item_from_order(order_id: str, menu_item_id: int, quantity: int = 1) -> None:
    """
    Remove an item from an order and restore inventory

    Args:
        order_id: The ID of the order
        menu_item_id: The ID of the menu item to remove
        quantity: The quantity to remove (default: 1)

    Raises:
        ValueError: If parameters are invalid or order/menu item not found
        RuntimeError: If there are issues removing the item
    """
    if quantity <= 0:
        raise ValueError('Quantity must be positive')

    try:
        order_obj = get_order(order_id)
        if not order_obj:
            raise ValueError(f'Order {order_id} not found')

        menu_item_obj = menu_utils.get_menu_item(menu_item_id=menu_item_id)
        if not menu_item_obj:
            raise ValueError(f'Menu item {menu_item_id} not found')

        existing_item = order_obj.find_order_item(menu_item_obj)
        if not existing_item:
            raise ValueError(f'Item {menu_item_obj.name} not found in order')

        if existing_item.quantity > quantity:
            existing_item.quantity -= quantity
            db_utils.update_model_instance(existing_item, quantity=existing_item.quantity)
            # Restore inventory for the removed quantity
            inventory_service.add_stock(menu_item_obj, quantity)
        else:
            # Restore all inventory for this item
            inventory_service.add_stock(menu_item_obj, existing_item.quantity)
            db_utils.delete_model_instance(existing_item)
    except Exception as e:
        logger.error(f'Error removing item from order {order_id}: {e!s}')
        raise RuntimeError(f'Failed to remove item from order: {e!s}')


def get_order_total(order_id: str) -> float:
    """
    Get the total price of an order

    Args:
        order_id: The ID of the order

    Returns:
        The total price of the order

    Raises:
        ValueError: If order_id is invalid or order not found
    """
    order_obj = get_order(order_id)
    if not order_obj:
        raise ValueError(f'Order {order_id} not found')
    return order_obj.total_price


def get_order_items(order_id: str) -> List[menu_item.MenuItem]:
    """
    Get all menu items in an order

    Args:
        order_id: The ID of the order

    Returns:
        List of menu items in the order

    Raises:
        ValueError: If order_id is invalid or order not found
    """
    order_obj = get_order(order_id)
    if not order_obj:
        raise ValueError(f'Order {order_id} not found')
    return order_obj.menu_items


def get_item_quantity(order_id: str, menu_item_id: int) -> int:
    """
    Get the quantity of a specific menu item in an order

    Args:
        order_id: The ID of the order
        menu_item_id: The ID of the menu item

    Returns:
        The quantity of the menu item in the order

    Raises:
        ValueError: If parameters are invalid or order/menu item not found
    """
    order_obj = get_order(order_id)
    if not order_obj:
        raise ValueError(f'Order {order_id} not found')

    menu_item_obj = menu_utils.get_menu_item(menu_item_id=menu_item_id)
    if not menu_item_obj:
        raise ValueError(f'Menu item {menu_item_id} not found')

    return order_obj.get_item_quantity(menu_item_obj)


@transaction.atomic
def cancel_order(order_id: str) -> None:
    """
    Cancel an order and restore inventory

    Args:
        order_id: The ID of the order to cancel

    Raises:
        ValueError: If order is not found or not in pending status
        RuntimeError: If there are issues cancelling the order
    """
    try:
        order_obj = get_order(order_id)
        if not order_obj:
            raise ValueError(f'Order {order_id} not found')

        if order_obj.status != 'pending':
            raise ValueError('Only pending orders can be cancelled')

        # Restore inventory for all items in the order
        for order_item in order_obj.items.all():
            try:
                inventory_service.add_stock(order_item.menu_item, order_item.quantity)
            except Exception as e:
                logger.error(f'Error restoring inventory for {order_item.menu_item.name}: {e!s}')
                # Continue with cancellation even if inventory restoration fails

        # Mark the order as cancelled
        order_obj.status = 'cancelled'
        db_utils.update_model_instance(order_obj, status='cancelled')
    except Exception as e:
        logger.error(f'Error cancelling order {order_id}: {e!s}')
        raise RuntimeError(f'Failed to cancel order: {e!s}')
