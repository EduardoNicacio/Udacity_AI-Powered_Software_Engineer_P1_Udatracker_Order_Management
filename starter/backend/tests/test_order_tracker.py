import pytest
from unittest.mock import Mock
from ..order_tracker import OrderTracker

# --- Fixtures for Unit Tests ---

@pytest.fixture
def mock_storage():
    """
    Provides a mock storage object for tests.
    This mock will be configured to simulate various storage behaviors.
    """
    mock = Mock()
    # By default, mock get_order to return None (no order found)
    mock.get_order.return_value = None
    # By default, mock get_all_orders to return an empty dict
    mock.get_all_orders.return_value = {}
    return mock

@pytest.fixture
def order_tracker(mock_storage):
    """
    Provides an OrderTracker instance initialized with the mock_storage.
    """
    return OrderTracker(mock_storage)

#
# --- add_order tests ---
#

def test_add_order_successfully(order_tracker, mock_storage):
    """Tests adding a new order with default 'pending' status."""
    order_tracker.add_order("ORD001", "Laptop", 1, "CUST001")

    # We expect save_order to be called once
    mock_storage.save_order.assert_called_once()

def test_add_order_raises_error_if_exists(order_tracker, mock_storage):
    """Tests that adding an order with a duplicate ID raises a ValueError."""
    # Simulate that the storage finds an existing order
    mock_storage.get_order.return_value = {"order_id": "ORD_EXISTING"}

    with pytest.raises(ValueError, match="Order with ID 'ORD_EXISTING' already exists."):
        order_tracker.add_order("ORD_EXISTING", "New Item", 1, "CUST001")

def test_add_order_stores_correct_details_and_default_status(order_tracker, mock_storage):
    """Tests that order details are stored correctly with status defaulting to 'pending'."""
    order_tracker.add_order("ORD002", "Mouse", 2, "CUST002")

    order_id, order_data = mock_storage.save_order.call_args.args
    assert order_id == "ORD002"
    assert order_data["order_id"] == "ORD002"
    assert order_data["item_name"] == "Mouse"
    assert order_data["quantity"] == 2
    assert order_data["customer_id"] == "CUST002"
    assert order_data["status"] == "pending"

def test_add_order_with_explicit_status(order_tracker, mock_storage):
    """Tests that an explicit valid status is honored when adding an order."""
    order_tracker.add_order("ORD003", "Keyboard", 1, "CUST003", status="shipped")

    order_data = mock_storage.save_order.call_args.args[1]
    assert order_data["status"] == "shipped"

def test_add_order_raises_error_for_invalid_quantity(order_tracker, mock_storage):
    """Tests that a non-positive quantity raises a ValueError."""
    with pytest.raises(ValueError, match="quantity"):
        order_tracker.add_order("ORD004", "Monitor", 0, "CUST004")

    with pytest.raises(ValueError, match="quantity"):
        order_tracker.add_order("ORD005", "Monitor", -3, "CUST004")

    mock_storage.save_order.assert_not_called()

def test_add_order_raises_error_for_missing_fields(order_tracker, mock_storage):
    """Tests that missing required fields raise a ValueError."""
    with pytest.raises(ValueError):
        order_tracker.add_order("", "Item", 1, "CUST001")

    with pytest.raises(ValueError):
        order_tracker.add_order("ORD006", "", 1, "CUST001")

    with pytest.raises(ValueError):
        order_tracker.add_order("ORD007", "Item", 1, "")

    mock_storage.save_order.assert_not_called()

def test_add_order_raises_error_for_invalid_status(order_tracker, mock_storage):
    """Tests that an invalid status value raises a ValueError."""
    with pytest.raises(ValueError, match="status"):
        order_tracker.add_order("ORD008", "Item", 1, "CUST001", status="lost")

    mock_storage.save_order.assert_not_called()

#
# --- get_order_by_id tests ---
#

def test_get_order_by_id_returns_existing_order(order_tracker, mock_storage):
    """Tests that fetching an existing order returns its details."""
    order = {
        "order_id": "GET001",
        "item_name": "Tablet",
        "quantity": 1,
        "customer_id": "CUST100",
        "status": "pending",
    }
    mock_storage.get_order.return_value = order

    result = order_tracker.get_order_by_id("GET001")
    assert result == order

def test_get_order_by_id_returns_none_for_missing_order(order_tracker):
    """Tests that a non-existent order ID returns None."""
    result = order_tracker.get_order_by_id("DOES_NOT_EXIST")
    assert result is None

def test_get_order_by_id_raises_error_for_empty_id(order_tracker):
    """Tests that an empty order ID raises a ValueError."""
    with pytest.raises(ValueError, match="order_id"):
        order_tracker.get_order_by_id("")

#
# --- update_order_status tests ---
#

def test_update_order_status_successfully(order_tracker, mock_storage):
    """Tests that an order's status can be updated from 'pending' to 'shipped'."""
    order = {
        "order_id": "UPD001",
        "item_name": "Router",
        "quantity": 1,
        "customer_id": "CUST200",
        "status": "pending",
    }
    mock_storage.get_order.return_value = order

    result = order_tracker.update_order_status("UPD001", "shipped")

    assert result["status"] == "shipped"
    # The updated order should have been saved back to storage
    saved_data = mock_storage.save_order.call_args.args[1]
    assert saved_data["status"] == "shipped"

def test_update_order_status_raises_error_for_invalid_status(order_tracker, mock_storage):
    """Tests that an invalid status raises a ValueError without reading storage."""
    with pytest.raises(ValueError, match="status"):
        order_tracker.update_order_status("UPD002", "lost")

    # Fail fast: no storage read should occur
    mock_storage.get_order.assert_not_called()

def test_update_order_status_raises_error_for_missing_order(order_tracker):
    """Tests that updating a non-existent order raises a ValueError."""
    with pytest.raises(ValueError, match="not found"):
        order_tracker.update_order_status("UPD003", "shipped")

def test_update_order_status_raises_error_for_empty_id(order_tracker):
    """Tests that an empty order ID raises a ValueError."""
    with pytest.raises(ValueError, match="order_id"):
        order_tracker.update_order_status("", "shipped")

#
# --- list_all_orders tests ---
#

def test_list_all_orders_returns_empty_list(order_tracker):
    """Tests that listing orders on empty storage returns an empty list."""
    assert order_tracker.list_all_orders() == []

def test_list_all_orders_returns_all_orders(order_tracker, mock_storage):
    """Tests that listing orders returns all stored orders."""
    mock_storage.get_all_orders.return_value = {
        "ORD_A": {"order_id": "ORD_A", "item_name": "A", "quantity": 1, "customer_id": "C1", "status": "pending"},
        "ORD_B": {"order_id": "ORD_B", "item_name": "B", "quantity": 2, "customer_id": "C2", "status": "shipped"},
    }

    orders = order_tracker.list_all_orders()
    assert len(orders) == 2

#
# --- list_orders_by_status tests ---
#

def test_list_orders_by_status_returns_matching_orders(order_tracker, mock_storage):
    """Tests that only orders with the requested status are returned."""
    mock_storage.get_all_orders.return_value = {
        "ORD_X": {"order_id": "ORD_X", "item_name": "X", "quantity": 1, "customer_id": "C1", "status": "pending"},
        "ORD_Y": {"order_id": "ORD_Y", "item_name": "Y", "quantity": 1, "customer_id": "C2", "status": "shipped"},
        "ORD_Z": {"order_id": "ORD_Z", "item_name": "Z", "quantity": 1, "customer_id": "C3", "status": "pending"},
    }

    pending_orders = order_tracker.list_orders_by_status("pending")
    assert len(pending_orders) == 2
    assert all(o["status"] == "pending" for o in pending_orders)

def test_list_orders_by_status_returns_empty_when_no_match(order_tracker, mock_storage):
    """Tests that no matching orders returns an empty list."""
    mock_storage.get_all_orders.return_value = {
        "ORD_M": {"order_id": "ORD_M", "item_name": "M", "quantity": 1, "customer_id": "C1", "status": "shipped"},
    }

    assert order_tracker.list_orders_by_status("pending") == []

def test_list_orders_by_status_returns_empty_on_empty_storage(order_tracker):
    """Tests that listing by status on empty storage returns an empty list."""
    assert order_tracker.list_orders_by_status("pending") == []

def test_list_orders_by_status_raises_error_for_invalid_status(order_tracker):
    """Tests that an invalid status raises a ValueError."""
    with pytest.raises(ValueError, match="status"):
        order_tracker.list_orders_by_status("lost")

    with pytest.raises(ValueError, match="status"):
        order_tracker.list_orders_by_status("")
