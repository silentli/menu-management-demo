from django.db import models


class MenuItem(models.Model):
    """
    Model representing a menu item in the restaurant.
    """
    CATEGORY_CHOICES = [
        ('appetizer', 'Appetizer'),
        ('main', 'Main Course'),
        ('dessert', 'Dessert'),
        ('beverage', 'Beverage'),
    ]

    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    name = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    sold_out = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} (${self.price})"

    class Meta:
        ordering = ['category', 'name']
