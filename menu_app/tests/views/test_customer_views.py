import pytest
from django.urls import reverse
from menu_app.models.order import Order

@pytest.mark.django_db
def test_menu_list_view(client, menu_item, test_data):
    """Test menu listing functionality."""
    response = client.get(reverse('menu_app:menu_list'))
    assert response.status_code == 200
    assert 'menus' in response.context
    assert 'categories' in response.context
    assert test_data['name'] in response.content.decode()
    assert str(test_data['price']) in response.content.decode()

@pytest.mark.django_db
def test_cart_management(client, menu_item, test_data):
    """Test cart management functionality."""
    # Test adding item to cart
    response = client.post(reverse('menu_app:menu_list'), {
        'menu_item_id': menu_item.id,
        'action': 'add'
    })
    assert response.status_code == 302
    
    # Check cart in session
    session = client.session
    assert 'cart' in session
    assert session['cart'][str(menu_item.id)] == 1
    
    # Test updating item quantity
    response = client.post(reverse('menu_app:menu_list'), {
        'menu_item_id': menu_item.id,
        'action': 'update',
        'quantity': 2
    })
    assert response.status_code == 302
    session = client.session
    assert session['cart'][str(menu_item.id)] == 2
    
    # Test removing item from cart
    response = client.post(reverse('menu_app:menu_list'), {
        'menu_item_id': menu_item.id,
        'action': 'remove'
    })
    assert response.status_code == 302
    
    # Check cart is empty
    session = client.session
    assert str(menu_item.id) not in session.get('cart', {})

@pytest.mark.django_db
def test_checkout_process(client, menu_item, inventory_item, test_data):
    """Test checkout process."""
    # Add item to cart and checkout
    client.post(reverse('menu_app:menu_list'), {
        'menu_item_id': menu_item.id,
        'action': 'add'
    })
    response = client.post(reverse('menu_app:menu_list'), {
        'action': 'checkout'
    })
    assert response.status_code == 302  # Redirect after checkout

    # Check cart is empty after checkout
    session = client.session
    session.save()  # Save the session to persist changes
    assert 'cart' not in session

    # Verify inventory was updated
    inventory_item.refresh_from_db()
    assert inventory_item.quantity == test_data['quantity'] - 1  # One item was ordered
