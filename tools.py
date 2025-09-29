"""
Database tools for CRUD operations with LangChain integration.
"""
from typing import Any, Dict, List, Optional
from langchain_core.tools import tool
from datetime import datetime
import json
from database import db


# ==================== READ OPERATIONS ====================

@tool
def search_orders(
    order_number: Optional[str] = None,
    customer_name: Optional[str] = None,
    status: Optional[str] = None
) -> str:
    """
    Search for orders in the database. Can filter by order number, customer name, or status.

    Args:
        order_number: Filter by order number (e.g., 'ORD-1001')
        customer_name: Filter by customer name (partial match supported)
        status: Filter by order status (e.g., 'Shipped', 'Processing', 'Delivered', 'Cancelled')

    Returns:
        JSON string with matching orders or error message
    """
    try:
        query = "SELECT * FROM orders WHERE 1=1"
        params = []

        if order_number:
            query += " AND order_number = ?"
            params.append(order_number)

        if customer_name:
            query += " AND customer_name LIKE ?"
            params.append(f"%{customer_name}%")

        if status:
            query += " AND status = ?"
            params.append(status)

        results = db.execute_query(query, tuple(params))

        if not results:
            return json.dumps({"success": False, "message": "No orders found matching the criteria."})

        return json.dumps({"success": True, "count": len(results), "orders": results})
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@tool
def search_products(
    product_name: Optional[str] = None,
    category: Optional[str] = None,
    max_price: Optional[float] = None
) -> str:
    """
    Search for products in the catalog. Can filter by name, category, or price.

    Args:
        product_name: Filter by product name (partial match supported)
        category: Filter by category (e.g., 'Electronics', 'Accessories')
        max_price: Filter by maximum price

    Returns:
        JSON string with matching products or error message
    """
    try:
        query = "SELECT * FROM products WHERE 1=1"
        params = []

        if product_name:
            query += " AND product_name LIKE ?"
            params.append(f"%{product_name}%")

        if category:
            query += " AND category = ?"
            params.append(category)

        if max_price:
            query += " AND price <= ?"
            params.append(max_price)

        results = db.execute_query(query, tuple(params))

        if not results:
            return json.dumps({"success": False, "message": "No products found matching the criteria."})

        return json.dumps({"success": True, "count": len(results), "products": results})
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@tool
def get_order_details(order_number: str) -> str:
    """
    Get detailed information about a specific order.

    Args:
        order_number: The order number to look up (e.g., 'ORD-1001')

    Returns:
        JSON string with order details or error message
    """
    try:
        results = db.execute_query(
            "SELECT * FROM orders WHERE order_number = ?",
            (order_number,)
        )

        if not results:
            return json.dumps({"success": False, "message": f"Order {order_number} not found."})

        return json.dumps({"success": True, "order": results[0]})
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


# ==================== CREATE OPERATIONS ====================

@tool
def create_order(
    customer_name: str,
    product_name: str,
    quantity: int,
    order_number: Optional[str] = None
) -> str:
    """
    Create a new order in the system. REQUIRES USER CONFIRMATION before execution.

    Args:
        customer_name: Name of the customer placing the order
        product_name: Name of the product to order
        quantity: Quantity to order
        order_number: Optional custom order number (auto-generated if not provided)

    Returns:
        JSON string with created order details or error message
    """
    try:
        # First, check if product exists and get price
        product_results = db.execute_query(
            "SELECT * FROM products WHERE product_name = ?",
            (product_name,)
        )

        if not product_results:
            return json.dumps({"success": False, "message": f"Product '{product_name}' not found in catalog."})

        product = product_results[0]

        # Check stock availability
        if product['stock'] < quantity:
            return json.dumps({
                "success": False,
                "message": f"Insufficient stock. Only {product['stock']} units available."
            })

        # Generate order number if not provided
        if not order_number:
            # Get max order number
            max_order = db.execute_query("SELECT MAX(order_number) as max_num FROM orders")
            if max_order[0]['max_num']:
                last_num = int(max_order[0]['max_num'].split('-')[1])
                order_number = f"ORD-{last_num + 1:04d}"
            else:
                order_number = "ORD-1001"

        now = datetime.now().isoformat()

        # Create the order
        db.execute_update("""
            INSERT INTO orders (order_number, customer_name, product_name, quantity, price, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (order_number, customer_name, product_name, quantity, product['price'], 'Processing', now, now))

        # Update product stock
        new_stock = product['stock'] - quantity
        db.execute_update(
            "UPDATE products SET stock = ? WHERE product_name = ?",
            (new_stock, product_name)
        )

        # Get the created order
        result = db.execute_query(
            "SELECT * FROM orders WHERE order_number = ?",
            (order_number,)
        )

        return json.dumps({
            "success": True,
            "message": f"Order {order_number} created successfully!",
            "order": result[0]
        })
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@tool
def add_product(
    product_name: str,
    price: float,
    stock: int,
    description: Optional[str] = None,
    category: Optional[str] = None
) -> str:
    """
    Add a new product to the catalog. REQUIRES USER CONFIRMATION before execution.

    Args:
        product_name: Name of the product
        price: Product price
        stock: Initial stock quantity
        description: Product description (optional)
        category: Product category (optional)

    Returns:
        JSON string with created product details or error message
    """
    try:
        # Check if product already exists
        existing = db.execute_query(
            "SELECT * FROM products WHERE product_name = ?",
            (product_name,)
        )

        if existing:
            return json.dumps({
                "success": False,
                "message": f"Product '{product_name}' already exists in the catalog."
            })

        now = datetime.now().isoformat()

        db.execute_update("""
            INSERT INTO products (product_name, description, price, stock, category, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (product_name, description or "", price, stock, category or "General", now))

        # Get the created product
        result = db.execute_query(
            "SELECT * FROM products WHERE product_name = ?",
            (product_name,)
        )

        return json.dumps({
            "success": True,
            "message": f"Product '{product_name}' added successfully!",
            "product": result[0]
        })
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


# ==================== UPDATE OPERATIONS ====================

@tool
def update_order_status(order_number: str, new_status: str) -> str:
    """
    Update the status of an existing order. REQUIRES USER CONFIRMATION before execution.

    Args:
        order_number: The order number to update (e.g., 'ORD-1001')
        new_status: New status (e.g., 'Processing', 'Shipped', 'Delivered', 'Cancelled')

    Returns:
        JSON string with update confirmation or error message
    """
    try:
        # Check if order exists
        existing = db.execute_query(
            "SELECT * FROM orders WHERE order_number = ?",
            (order_number,)
        )

        if not existing:
            return json.dumps({
                "success": False,
                "message": f"Order {order_number} not found."
            })

        now = datetime.now().isoformat()

        affected = db.execute_update(
            "UPDATE orders SET status = ?, updated_at = ? WHERE order_number = ?",
            (new_status, now, order_number)
        )

        # Get updated order
        result = db.execute_query(
            "SELECT * FROM orders WHERE order_number = ?",
            (order_number,)
        )

        return json.dumps({
            "success": True,
            "message": f"Order {order_number} status updated to '{new_status}'.",
            "order": result[0]
        })
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@tool
def update_product_price(product_name: str, new_price: float) -> str:
    """
    Update the price of a product. REQUIRES USER CONFIRMATION before execution.

    Args:
        product_name: Name of the product to update
        new_price: New price for the product

    Returns:
        JSON string with update confirmation or error message
    """
    try:
        # Check if product exists
        existing = db.execute_query(
            "SELECT * FROM products WHERE product_name = ?",
            (product_name,)
        )

        if not existing:
            return json.dumps({
                "success": False,
                "message": f"Product '{product_name}' not found."
            })

        db.execute_update(
            "UPDATE products SET price = ? WHERE product_name = ?",
            (new_price, product_name)
        )

        # Get updated product
        result = db.execute_query(
            "SELECT * FROM products WHERE product_name = ?",
            (product_name,)
        )

        return json.dumps({
            "success": True,
            "message": f"Product '{product_name}' price updated to ${new_price:.2f}.",
            "product": result[0]
        })
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@tool
def update_product_stock(product_name: str, new_stock: int) -> str:
    """
    Update the stock quantity of a product. REQUIRES USER CONFIRMATION before execution.

    Args:
        product_name: Name of the product to update
        new_stock: New stock quantity

    Returns:
        JSON string with update confirmation or error message
    """
    try:
        # Check if product exists
        existing = db.execute_query(
            "SELECT * FROM products WHERE product_name = ?",
            (product_name,)
        )

        if not existing:
            return json.dumps({
                "success": False,
                "message": f"Product '{product_name}' not found."
            })

        db.execute_update(
            "UPDATE products SET stock = ? WHERE product_name = ?",
            (new_stock, product_name)
        )

        # Get updated product
        result = db.execute_query(
            "SELECT * FROM products WHERE product_name = ?",
            (product_name,)
        )

        return json.dumps({
            "success": True,
            "message": f"Product '{product_name}' stock updated to {new_stock} units.",
            "product": result[0]
        })
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


# ==================== DELETE OPERATIONS ====================

@tool
def cancel_order(order_number: str) -> str:
    """
    Cancel an order and restore product stock. REQUIRES USER CONFIRMATION before execution.

    Args:
        order_number: The order number to cancel (e.g., 'ORD-1001')

    Returns:
        JSON string with cancellation confirmation or error message
    """
    try:
        # Get order details
        order_results = db.execute_query(
            "SELECT * FROM orders WHERE order_number = ?",
            (order_number,)
        )

        if not order_results:
            return json.dumps({
                "success": False,
                "message": f"Order {order_number} not found."
            })

        order = order_results[0]

        # Restore stock
        db.execute_update(
            "UPDATE products SET stock = stock + ? WHERE product_name = ?",
            (order['quantity'], order['product_name'])
        )

        # Update order status to Cancelled instead of deleting
        now = datetime.now().isoformat()
        db.execute_update(
            "UPDATE orders SET status = 'Cancelled', updated_at = ? WHERE order_number = ?",
            (now, order_number)
        )

        return json.dumps({
            "success": True,
            "message": f"Order {order_number} has been cancelled. Stock restored."
        })
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@tool
def delete_product(product_name: str) -> str:
    """
    Remove a product from the catalog. REQUIRES USER CONFIRMATION before execution.
    WARNING: This will permanently delete the product.

    Args:
        product_name: Name of the product to delete

    Returns:
        JSON string with deletion confirmation or error message
    """
    try:
        # Check if product exists
        existing = db.execute_query(
            "SELECT * FROM products WHERE product_name = ?",
            (product_name,)
        )

        if not existing:
            return json.dumps({
                "success": False,
                "message": f"Product '{product_name}' not found."
            })

        # Check if there are active orders for this product
        active_orders = db.execute_query(
            "SELECT COUNT(*) as count FROM orders WHERE product_name = ? AND status != 'Cancelled' AND status != 'Delivered'",
            (product_name,)
        )

        if active_orders[0]['count'] > 0:
            return json.dumps({
                "success": False,
                "message": f"Cannot delete '{product_name}'. There are {active_orders[0]['count']} active orders for this product."
            })

        db.execute_update(
            "DELETE FROM products WHERE product_name = ?",
            (product_name,)
        )

        return json.dumps({
            "success": True,
            "message": f"Product '{product_name}' has been removed from the catalog."
        })
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


# Export all tools
ALL_TOOLS = [
    search_orders,
    search_products,
    get_order_details,
    create_order,
    add_product,
    update_order_status,
    update_product_price,
    update_product_stock,
    cancel_order,
    delete_product,
]