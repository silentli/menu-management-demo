from typing import ClassVar, List, Tuple

from django.db import models


class MenuItem(models.Model):
    """
    Represents a menu item with its details.
    """

    CATEGORY_CHOICES: ClassVar[List[Tuple[str, str]]] = [
        ('appetizer', 'Appetizer'),
        ('main', 'Main Course'),
        ('dessert', 'Dessert'),
        ('beverage', 'Beverage'),
    ]

    # Fields
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    name = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        ordering: ClassVar[List[str]] = ['category', 'name']

    def __str__(self):
        return f'{self.name} (${self.price})'

    @property
    def is_available(self):
        """Check if the menu item is available (has inventory and not sold out)."""
        return hasattr(self, 'inventory') and not self.inventory.is_sold_out
