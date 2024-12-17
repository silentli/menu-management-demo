import re
from typing import Callable
from app.models.order import Order
from app.managers.menu_manager import MenuManager
from app.managers.inventory_manager import InventoryManager
from app.managers.order_manager import OrderManager
from app.utils.fuzzy_match import find_fuzzy_menu_item


# Command registry dictionary
COMMAND_REGISTRY: dict[str, Callable] = {}

def register_command(name: str):
    """
    decorator to register a command handler into the COMMAND_REGISTRY dictionary
    """
    def decorator(func: Callable):
        COMMAND_REGISTRY[name] = func
        return func
    return decorator

def parse_command(command: str) -> tuple[str | None, int | None, str | None]:
    """
    parses user commands into actionable components
    supports commands like 'add 2 tea' or 'remove 1 dumpling'

    returns:
        tuple: (action, quantity, item_name) or (action, None, None) for single-word commands like 'summary' or 'done'
    """
    command = command.strip().lower()

    if command in {"summary", "done", "cancel"}:
        return command, None, None

    match = re.match(r"(add|remove)\s+(\d+)\s+(.+)", command)
    if match:
        action, quantity, item_name = match.groups()
        return action, int(quantity), item_name.strip()

    return None, None, None

@register_command("add")
def handle_add(
    order: Order,
    menu_manager: MenuManager,
    inventory_manager: InventoryManager,
    item_name: str,
    quantity: int
) -> None:
    """handles adding an item to the order, ensuring inventory constraints"""
    menu_item = menu_manager.get_menu_item_by_name(item_name)
    if not menu_item:
        print(f"'{item_name}' is not on the menu. Please try again.")
        return

    total_quantity = order.get_item_quantity(menu_item) + quantity

    if not inventory_manager.check_availability_by_id(menu_item.id, total_quantity):
        print(f"Unable to add {quantity} x {menu_item.name}. Not enough stock available.")
        return

    order.add_item(menu_item, quantity)
    print(f"Added {quantity} x {menu_item.name} to the order.")


@register_command("remove")
def handle_remove(order: Order, item_name: str, quantity: int) -> None:
    """handles removing an item from the order, with typo-tolerant name matching"""
    menu_item = find_fuzzy_menu_item(item_name, order.menu_items)

    if not menu_item:
        print(f"No item named '{item_name}' in the order. Please check the name and try again.")
        return

    # note: If the customer specifies a quantity greater than the current amount of the item in the order,
    # the entire item is removed without notifying the customer. Correcting the user is unnecessary here,
    # as the result (removing the item) aligns with their intent.
    order.remove_item(menu_item, quantity)
    print(f"Removed {quantity} x {menu_item.name} from the order.")


@register_command("summary")
def handle_summary(order: Order) -> None:
    """
    handles displaying the order summary
    """
    print("Order Summary:")
    for order_item in order.order_items:
        total = order_item.menu_item.price * order_item.quantity
        print(f"{order_item.quantity} x {order_item.menu_item.name} @ ${order_item.menu_item.price:.2f} = ${total:.2f}")
    print(f"Total Price: ${order.total_price:.2f}")


@register_command("cancel")
def handle_cancel(order: Order, order_manager: OrderManager) -> None:
    """
    handles canceling the current order
    """
    order_manager.cancel_order(order)
    print("The order has been canceled. Welcome back next time!")


@register_command("done")
def handle_finalize(order: Order, order_manager: OrderManager) -> None:
    """
    handles finalizing the order
    """
    if not order.order_items:
        print("No items in the order. Cannot finalize.")
        return

    print("Finalizing Order:")
    handle_summary(order)

    confirm = input("Confirm order? (yes/no): ").strip().lower()
    if confirm == "yes":
        order_manager.save_order(order)
        print("Order confirmed. Thank you!")
    else:
        print("Order canceled.")


def order_workflow(menu_manager: MenuManager, inventory_manager: InventoryManager, order_manager: OrderManager) -> None:
    order = order_manager.initialize_order()

    while True:
        command = input("Enter your command (e.g., 'add 2 tea', 'remove 1 dumpling', 'summary', 'cancel', 'done'): ").strip()

        action, quantity, item_name = parse_command(command)

        command_handler = COMMAND_REGISTRY.get(action)
        if not command_handler:
            print("Invalid command. Try 'add 2 tea', 'remove 1 dumpling', 'summary', 'cancel', or 'done'.")
            continue

        if action in ["done", "cancel"]:
            command_handler(order, order_manager)
            break
        elif action == "summary":
            command_handler(order)
        else:
            command_handler(order, menu_manager, inventory_manager, item_name, quantity)
