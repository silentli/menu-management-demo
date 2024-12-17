import difflib
from app.models.menu_item import MenuItem

def find_fuzzy_menu_item(user_input: str, menu_items: list[MenuItem], cutoff: float = 0.6) -> MenuItem | None:
    """
    finds the closest matching MenuItem from a list of MenuItems based on the user input

    returns:
        MenuItem | None: The closest matching MenuItem, or None if no match is found.
    """
    menu_item_names = [item.name for item in menu_items]
    close_matches = difflib.get_close_matches(user_input, menu_item_names, n=1, cutoff=cutoff)

    if not close_matches:
        return None

    closest_name = close_matches[0]
    return next((item for item in menu_items if item.name == closest_name), None)
