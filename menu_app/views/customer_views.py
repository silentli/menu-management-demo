from django.views import View
from django.views.generic import ListView
from django.shortcuts import redirect
from django.contrib import messages

from menu_app.models.menu_item import MenuItem
from menu_app.models.order import Order
from menu_app.services import menu_service, order_service

class MenuListView(ListView):
    """View for customers to browse the menu and place orders"""
    model = MenuItem
    template_name = 'menu_app/menu_list.html'
    context_object_name = 'menus'
    
    def get_queryset(self):
        category = self.request.GET.get('category')
        return menu_service.get_menu(category=category)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = MenuItem.CATEGORY_CHOICES
        
        # Get cart from session
        cart = self.request.session.get('cart', {})
        if cart:
            # Calculate total price and get menu items
            total_price = 0
            cart_items = []
            for menu_item_id, quantity in cart.items():
                menu_item = menu_service.get_menu_item(menu_item_id=menu_item_id)
                if menu_item:
                    item_total = menu_item.price * quantity
                    total_price += item_total
                    cart_items.append({
                        'menu_item': menu_item,
                        'quantity': quantity,
                        'total_price': item_total
                    })
            
            context['cart_items'] = cart_items
            context['cart_total'] = total_price
            
        return context
    
    def post(self, request):
        """Handle cart actions"""
        try:
            menu_item_id = request.POST.get('menu_item_id')
            action = request.POST.get('action')
            
            # Initialize cart if not exists
            if 'cart' not in request.session:
                request.session['cart'] = {}
            
            cart = request.session['cart']
            
            if action == 'add':
                # Add item to cart
                cart[menu_item_id] = cart.get(menu_item_id, 0) + 1
                messages.success(request, 'Item added to cart!')
                request.session.modified = True
                
            elif action == 'decrease':
                # Decrease item quantity
                if menu_item_id in cart and cart[menu_item_id] > 1:
                    cart[menu_item_id] -= 1
                    messages.success(request, 'Item quantity decreased!')
                elif menu_item_id in cart:
                    del cart[menu_item_id]
                    messages.success(request, 'Item removed from cart!')
                request.session.modified = True
                
            elif action == 'remove':
                # Remove item from cart
                if menu_item_id in cart:
                    del cart[menu_item_id]
                    messages.success(request, 'Item removed from cart!')
                request.session.modified = True
                    
            elif action == 'update':
                # Update item quantity
                quantity = int(request.POST.get('quantity', 1))
                if quantity > 0:
                    cart[menu_item_id] = quantity
                    messages.success(request, 'Cart updated!')
                else:
                    del cart[menu_item_id]
                    messages.success(request, 'Item removed from cart!')
                request.session.modified = True
                    
            elif action == 'checkout':
                # Create order from cart
                if cart:
                    try:
                        # Create new order
                        new_order = order_service.create_order()
                        
                        # Add items to order
                        for menu_item_id, quantity in cart.items():
                            order_service.add_item_to_order(new_order.id, int(menu_item_id), quantity)
                        
                        messages.success(request, 'Order placed successfully!')
                    except Exception as e:
                        messages.error(request, f'Error processing order: {str(e)}')
                    finally:
                        # Clear cart regardless of success or failure
                        del request.session['cart']
                        request.session.modified = True
                    return redirect('menu_app:menu_list')
                else:
                    messages.warning(request, 'Your cart is empty!')
            
            # Save cart to session
            request.session['cart'] = cart
            request.session.modified = True
                
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            
        return redirect('menu_app:menu_list')
