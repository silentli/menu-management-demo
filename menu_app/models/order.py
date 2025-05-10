import logging
from decimal import Decimal
from typing import ClassVar, List, Tuple

from django.db import models

from menu_app.models.menu_item import MenuItem

logger = logging.getLogger(__name__)


class Order(models.Model):
    """
    Represents a customer order with its items and status.
    """

    STATUS_CHOICES: ClassVar[List[Tuple[str, str]]] = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    # Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    class Meta:
        ordering: ClassVar[List[str]] = ['-created_at']

    def __str__(self):
        return f'Order {self.id} ({self.status})'

    def clean(self):
        """Validate the order."""
        if self.status not in dict(self.STATUS_CHOICES):
            raise ValueError('Invalid status')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def is_modifiable(self):
        """Check if the order can be modified."""
        return self.status == 'pending'

    def complete(self):
        """Mark the order as completed"""
        if self.status != 'pending':
            raise ValueError('Only pending orders can be completed')
        self.status = 'completed'
        self.save()

    def cancel(self):
        """Mark the order as cancelled"""
        if self.status != 'pending':
            raise ValueError('Only pending orders can be cancelled')
        self.status = 'cancelled'
        self.save()

    def find_order_item(self, menu_item):
        """
        Find an existing order item for a given menu item.

        Args:
            menu_item: The MenuItem to find in the order

        Returns:
            OrderItem if found, None otherwise

        Raises:
            ValueError: If order is not modifiable
        """
        if not self.is_modifiable():
            raise ValueError('Cannot modify a completed or cancelled order')

        try:
            return self.items.get(menu_item=menu_item)
        except OrderItem.DoesNotExist:
            return None

    @property
    def total_price(self) -> Decimal:
        """Calculate the total price of the order."""
        return sum(item.subtotal for item in self.items.all())


class OrderItem(models.Model):
    """
    Represents an item within an order.
    """

    # Fields
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price_at_time_of_order = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'
        ordering: ClassVar[List[str]] = ['order', 'menu_item__name']
        unique_together: ClassVar[List[str]] = ['order', 'menu_item']

    def __str__(self):
        return f'{self.quantity} x {self.menu_item.name} (${self.subtotal})'

    def clean(self):
        """Validate the order item."""
        if self.quantity <= 0:
            raise ValueError('Quantity must be positive')
        if self.price_at_time_of_order <= 0:
            raise ValueError('Price must be positive')

    def save(self, *args, **kwargs):
        # Store the price at the time of ordering if not already set
        if not self.price_at_time_of_order:
            self.price_at_time_of_order = self.menu_item.price
        self.clean()
        super().save(*args, **kwargs)

    @property
    def subtotal(self) -> Decimal:
        """Calculate the subtotal for this item."""
        return self.quantity * self.price_at_time_of_order
