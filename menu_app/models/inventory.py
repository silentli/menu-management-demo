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

    def __str__(self):
        return f"{self.menu_item.name} - {self.quantity} available"

    class Meta:
        verbose_name = "Inventory Item"
        verbose_name_plural = "Inventory Items"
        ordering = ['menu_item__category', 'menu_item__name']

    def is_low_stock(self, threshold=5):
        """Check if the item is low in stock"""
        return self.quantity < threshold
