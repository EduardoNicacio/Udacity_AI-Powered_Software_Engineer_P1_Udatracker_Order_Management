# This module contains the OrderTracker class, which encapsulates the core
# business logic for managing orders.

class OrderTracker:
    """
    Manages customer orders, providing functionalities to add, update,
    and retrieve order information.
    """
    VALID_STATUSES = {"pending", "processing", "shipped", "delivered", "cancelled"}

    def __init__(self, storage):
        required_methods = ['save_order', 'get_order', 'get_all_orders']
        for method in required_methods:
            if not hasattr(storage, method) or not callable(getattr(storage, method)):
                raise TypeError(f"Storage object must implement a callable '{method}' method.")
        self.storage = storage

    def _validate_order_fields(self, order_id, item_name, quantity, customer_id, status):
        """Raises a ValueError if any order field is missing or invalid."""
        if not order_id:
            raise ValueError("order_id must be a non-empty string.")
        if not item_name:
            raise ValueError("item_name must be a non-empty string.")
        if not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("quantity must be a positive integer.")
        if not customer_id:
            raise ValueError("customer_id must be a non-empty string.")
        if status not in self.VALID_STATUSES:
            raise ValueError(f"status '{status}' is invalid. Must be one of: {sorted(self.VALID_STATUSES)}")

    def add_order(self, order_id: str, item_name: str, quantity: int, customer_id: str, status: str = "pending"):
        """Adds a new order, raising a ValueError if the ID is a duplicate or input is invalid."""
        self._validate_order_fields(order_id, item_name, quantity, customer_id, status)

        if self.storage.get_order(order_id):
            raise ValueError(f"Order with ID '{order_id}' already exists.")

        order_data = {
            "order_id": order_id,
            "item_name": item_name,
            "quantity": quantity,
            "customer_id": customer_id,
            "status": status,
        }
        self.storage.save_order(order_id, order_data)
        return order_data

    def get_order_by_id(self, order_id: str):
        """Returns the order matching order_id, or None if it does not exist."""
        if not order_id:
            raise ValueError("order_id must be a non-empty string.")
        return self.storage.get_order(order_id)

    def update_order_status(self, order_id: str, new_status: str):
        """Updates an order's status, raising a ValueError for invalid status or a missing order."""
        if not order_id:
            raise ValueError("order_id must be a non-empty string.")
        if new_status not in self.VALID_STATUSES:
            raise ValueError(f"status '{new_status}' is invalid. Must be one of: {sorted(self.VALID_STATUSES)}")

        order = self.storage.get_order(order_id)
        if order is None:
            raise ValueError(f"Order with ID '{order_id}' not found.")

        updated_order = order.copy()
        updated_order["status"] = new_status
        self.storage.save_order(order_id, updated_order)
        return updated_order

    def list_all_orders(self):
        """Returns all orders as a list of dictionaries."""
        return list(self.storage.get_all_orders().values())

    def list_orders_by_status(self, status: str):
        """Returns only the orders whose status matches the given status."""
        if status not in self.VALID_STATUSES:
            raise ValueError(f"status '{status}' is invalid. Must be one of: {sorted(self.VALID_STATUSES)}")
        return [order for order in self.list_all_orders() if order["status"] == status]
