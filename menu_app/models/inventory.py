from django.db import models
from menu_app.models.menu_item import MenuItem


class InventoryItem(models.Model):
    """
    Model representing inventory for a menu item.
    Tracks quantity of each item available in stock.
    """
    menu_item = models.OneToOneField(
        MenuItem, 
        on_delete=models.CASCADE,
        related_name='inventory'
    )
    quantity = models.PositiveIntegerField(default=0)

    @property
    def is_sold_out(self):
        """Check if the item is sold out"""
        return self.quantity == 0

    @property
    def is_low_stock(self):
        """Check if the item is low in stock"""
        return self.quantity < 5  # Default threshold

    def mark_sold_out(self):
        """Mark the item as sold out by setting quantity to 0"""
        self.quantity = 0
        self.save()

    def add_stock(self, amount):
        """Add stock to the inventory"""
        if amount < 0:
            raise ValueError("Cannot add negative stock")
        self.quantity += amount
        self.save()

    def remove_stock(self, amount):
        """Remove stock from the inventory"""
        if amount < 0:
            raise ValueError("Cannot remove negative stock")
        if amount > self.quantity:
            raise ValueError("Cannot remove more stock than available")
        self.quantity -= amount
        self.save()

    def __str__(self):
        return f"{self.menu_item.name} - {self.quantity} available"

    class Meta:
        verbose_name = "Inventory Item"
        verbose_name_plural = "Inventory Items"
        ordering = ['menu_item__category', 'menu_item__name']
