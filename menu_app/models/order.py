from django.db import models
from menu_app.models.menu_item import MenuItem


class Order(models.Model):
    """
    Model representing a customer order.
    Tracks order status and contains multiple order items.
    """

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending'
    )

    class Meta:
        ordering = ['-created_at']

    def is_modifiable(self):
        """Check if the order can be modified"""
        return self.status == 'pending'

    def complete(self):
        """Mark the order as completed"""
        if self.status != 'pending':
            return False
        self.status = 'completed'
        self.save()
        return True

    def cancel(self):
        """Mark the order as cancelled"""
        if self.status != 'pending':
            return False
        self.status = 'cancelled'
        self.save()
        return True

    @property
    def total_price(self):
        """Calculate the total price of the order"""
        return sum(order_item.subtotal for order_item in self.items.all())

    # Special methods
    def __str__(self):
        return f"Order {self.id} ({self.status})"


class OrderItem(models.Model):
    """
    Model representing a specific item in an order.
    Links menu items to orders with quantity.
    """

    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE, 
        related_name='items'
    )
    menu_item = models.ForeignKey(
        MenuItem, 
        on_delete=models.PROTECT
    )
    quantity = models.PositiveIntegerField(default=1)
    price_at_time_of_order = models.DecimalField(
        max_digits=6, 
        decimal_places=2
    )

    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"
        ordering = ['order', 'menu_item__name']

    @property
    def subtotal(self):
        """Calculate the subtotal for this item"""
        return self.price_at_time_of_order * self.quantity

    def save(self, *args, **kwargs):
        # Store the price at the time of ordering if not already set
        if not self.price_at_time_of_order:
            self.price_at_time_of_order = self.menu_item.price
        super().save(*args, **kwargs)

    # Special methods
    def __str__(self):
        return f"{self.quantity} x {self.menu_item.name}"
