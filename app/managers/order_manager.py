import logging
import os
import csv
from datetime import datetime
from app.models.order import Order

logger = logging.getLogger(__name__)


class OrderManager:
    def __init__(self, order_records_dir: str = "data/order_history"):
        """
        order_records_dir: directory to save daily order history files
        active_orders: tracks currently active orders
        """
        self.order_records_dir = order_records_dir
        self.active_orders = {}
        os.makedirs(order_records_dir, exist_ok=True)

    @staticmethod
    def generate_order_id() -> str:
        """generates a unique order ID based on the current timestamp in milliseconds"""
        return datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3]

    def _get_daily_file_path(self) -> str:
        today_date = datetime.now().strftime("%Y_%m_%d")
        return os.path.join(self.order_records_dir, f"{today_date}.csv")

    def initialize_order(self) -> Order:
        order_id = self.generate_order_id()
        new_order = Order(id=order_id)
        self.active_orders[order_id] = new_order
        return new_order

    def _stop_tracking_order(self, order_id: str) -> None:
        """stops tracking the order by removing it from active orders"""
        if order_id in self.active_orders:
            del self.active_orders[order_id]
            logger.debug(f"Order {order_id} has been untracked successfully.")
        else:
            logger.debug(f"Order {order_id} was not found in active orders.")

    def save_order(self, order: Order) -> None:
        """
        saves the order to a daily CSV file. Each MenuItem is saved as a separate row
        removes the order from active tracking
        """
        file_path = self._get_daily_file_path()
        fieldnames = ["order_id", "item_name", "price", "quantity"]
        rows = [
            {
                "order_id": order.id,
                "item_name": order_item.menu_item.name,
                "price": order_item.menu_item.price,
                "quantity": order_item.quantity,
            }
            for order_item in order.order_items
        ]

        file_exists = os.path.isfile(file_path)
        with open(file_path, mode="a", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            # write header if file is new
            if not file_exists:
                writer.writeheader()

            writer.writerows(rows)

        self._stop_tracking_order(order.id)
        logger.debug(f"Order {order.id} saved to {file_path} and removed from active tracking.")

    def cancel_order(self, order: Order) -> None:
        """
        cancels an active order and removes it from tracking.
        """
        self._stop_tracking_order(order.id)
        logger.debug(f"Order {order.id} canceled and removed from active tracking.")
