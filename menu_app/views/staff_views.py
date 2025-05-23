import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    UpdateView,
)
from django.views.generic.base import RedirectView

from menu_app.forms import MenuForm
from menu_app.models.inventory import InventoryItem
from menu_app.models.menu_item import MenuItem
from menu_app.models.order import Order
from menu_app.services import inventory_service, menu_service, order_service

logger = logging.getLogger(__name__)


class StaffLoginView(View):
    """View for staff login"""

    template_name = 'menu_app/staff/login.html'

    def get(self, request):
        if request.user.is_authenticated and request.user.is_staff:
            return redirect('menu_app:staff_dashboard')
        return render(request, self.template_name)

    def post(self, request):
        password = request.POST.get('password')

        # Get or create staff user
        staff_user, created = User.objects.get_or_create(
            username='staff', defaults={'is_staff': True, 'is_active': True}
        )

        # Always ensure the staff user has the correct password
        if created or not staff_user.check_password(settings.STAFF_PASSWORD):
            staff_user.set_password(settings.STAFF_PASSWORD)
            staff_user.save()

        # Check if the provided password matches
        if password == settings.STAFF_PASSWORD:
            # Log the user in
            login(request, staff_user)
            messages.success(request, 'Staff login successful!')
            return redirect('menu_app:staff_dashboard')

        messages.error(request, 'Invalid password')
        return render(request, self.template_name)


class StaffDashboardView(LoginRequiredMixin, View):
    """View for staff dashboard"""

    template_name = 'menu_app/staff/dashboard.html'
    login_url = 'menu_app:staff_login'

    def get(self, request):
        if not request.user.is_staff:
            return redirect('menu_app:staff_login')

        # Get all orders for the dashboard
        orders = order_service.get_all_orders()
        return render(request, self.template_name, {'orders': orders})


# Staff views
class StaffMenuListView(LoginRequiredMixin, ListView):
    """View for staff to manage menu items"""

    model = MenuItem
    template_name = 'menu_app/staff/menu_list.html'
    context_object_name = 'menus'

    def get(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('staff_login')
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = menu_service.get_menu()
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category=category)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = MenuItem.CATEGORY_CHOICES
        context['current_category'] = self.request.GET.get('category')
        return context


class StaffMenuCreateView(LoginRequiredMixin, CreateView):
    """View for staff to create new menu items"""

    model = MenuItem
    form_class = MenuForm
    template_name = 'menu_app/staff/menu_form.html'
    success_url = reverse_lazy('staff_menu_list')

    def get(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('staff_login')
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        try:
            menu_service.add_menu_item(
                name=form.cleaned_data['name'],
                price=form.cleaned_data['price'],
                category=form.cleaned_data['category'],
            )
            messages.success(self.request, 'Menu item created successfully.')
            return redirect(self.success_url)
        except Exception as e:
            messages.error(self.request, f'Error creating menu item: {e!s}')
            return self.form_invalid(form)


class StaffMenuUpdateView(LoginRequiredMixin, UpdateView):
    """View for staff to update menu items"""

    model = MenuItem
    form_class = MenuForm
    template_name = 'menu_app/staff/menu_form.html'
    success_url = reverse_lazy('staff_menu_list')

    def get(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('staff_login')
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        try:
            menu_service.modify_menu_item(
                menu_item=self.object,
                name=form.cleaned_data['name'],
                price=form.cleaned_data['price'],
                category=form.cleaned_data['category'],
            )
            messages.success(self.request, 'Menu item updated successfully.')
            return redirect(self.success_url)
        except Exception as e:
            messages.error(self.request, f'Error updating menu item: {e!s}')
            return self.form_invalid(form)


class StaffMenuDeleteView(LoginRequiredMixin, DeleteView):
    """View for staff to delete menu items"""

    model = MenuItem
    template_name = 'menu_app/staff/menu_confirm_delete.html'
    success_url = reverse_lazy('staff_menu_list')

    def get(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('staff_login')
        return super().get(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        try:
            menu_item = self.get_object()
            menu_item.delete()
            messages.success(request, 'Menu item deleted successfully.')
            return redirect(self.success_url)
        except Exception as e:
            messages.error(request, f'Error deleting menu item: {e!s}')
            return redirect(self.success_url)


# Inventory Management Views
class InventoryListView(LoginRequiredMixin, ListView):
    """View for staff to manage inventory"""

    model = InventoryItem
    template_name = 'menu_app/staff/inventory_list.html'
    context_object_name = 'inventory_items'

    def get(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('staff_login')
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return inventory_service.get_all_inventory_items()


class LowStockListView(LoginRequiredMixin, ListView):
    """View for staff to check low stock items"""

    model = InventoryItem
    template_name = 'menu_app/staff/low_stock_list.html'
    context_object_name = 'low_stock_items'

    def get(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('staff_login')
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        threshold = int(self.request.GET.get('threshold', 10))
        return inventory_service.get_low_stock_items(threshold)


class InventoryUpdateView(LoginRequiredMixin, View):
    """View for staff to update inventory"""

    def post(self, request, menu_item_id):
        if not request.user.is_staff:
            return redirect('menu_app:staff_login')

        try:
            menu_item = MenuItem.objects.get(id=menu_item_id)
            quantity = int(request.POST.get('quantity', 0))

            # Calculate quantity change from current inventory
            current_inventory = inventory_service.get_inventory(menu_item)
            current_quantity = current_inventory.quantity if current_inventory else 0
            quantity_change = quantity - current_quantity

            inventory_service.update_inventory(menu_item, quantity_change)
            messages.success(request, f'Inventory updated for {menu_item.name}')
        except MenuItem.DoesNotExist:
            messages.error(request, 'Menu item not found')
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Error updating inventory: {e!s}')

        return redirect('menu_app:inventory_list')


# Order Management Views
class StaffOrderListView(LoginRequiredMixin, ListView):
    """View for staff to view all orders"""

    model = Order
    template_name = 'menu_app/staff/order_list.html'
    context_object_name = 'orders'

    def get(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('staff_login')
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return order_service.get_all_orders()


class StaffOrderDetailView(LoginRequiredMixin, View):
    """View for staff to view order details"""

    template_name = 'menu_app/staff/order_detail.html'

    def get(self, request, pk):
        if not request.user.is_staff:
            return redirect('staff_login')

        order = order_service.get_order(pk)
        if not order:
            messages.error(request, 'Order not found.')
            return redirect('staff_order_list')

        context = {'order': order}
        return render(request, self.template_name, context)

    def post(self, request, pk):
        if not request.user.is_staff:
            return redirect('staff_login')

        try:
            action = request.POST.get('action')
            if action == 'cancel':
                order_service.cancel_order(pk)
                messages.success(request, 'Order cancelled successfully.')
            elif action == 'complete':
                order = order_service.get_order(pk)
                if order and order.status == 'pending':
                    order.complete()
                    messages.success(request, 'Order completed successfully.')
                else:
                    messages.error(request, 'Cannot complete a non-pending order.')
            else:
                messages.error(request, 'Invalid action.')
        except Exception as e:
            messages.error(request, f'Error processing order: {e!s}')

        return redirect('staff_order_list')


class StaffLogoutView(View):
    """View for staff logout"""

    def get(self, request):
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
        return redirect('staff_login')


class StaffRootRedirectView(RedirectView):
    permanent = False
    pattern_name = 'staff_dashboard'
