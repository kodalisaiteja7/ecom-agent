"""
Database initialization and schema for e-commerce customer support system.
"""
import sqlite3
from typing import Optional, List, Dict, Any
from datetime import datetime
import json


class EcommerceDB:
    """Handles SQLite database operations for e-commerce system."""

    def __init__(self, db_path: str = "ecommerce.db"):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        """Get database connection."""
        return sqlite3.connect(self.db_path)

    def init_db(self):
        """Initialize database with schema."""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Create orders table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_number TEXT UNIQUE NOT NULL,
                customer_name TEXT NOT NULL,
                product_name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        # Create products table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT UNIQUE NOT NULL,
                description TEXT,
                price REAL NOT NULL,
                stock INTEGER NOT NULL,
                category TEXT,
                created_at TEXT NOT NULL
            )
        """)

        conn.commit()
        conn.close()

        # Seed initial data if empty
        self.seed_initial_data()

    def seed_initial_data(self):
        """Add some initial sample data."""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Check if data already exists
        cursor.execute("SELECT COUNT(*) FROM products")
        if cursor.fetchone()[0] == 0:
            # Add sample products
            products = [
                ("Laptop Pro 15", "High-performance laptop with 16GB RAM", 1299.99, 25, "Electronics"),
                ("Wireless Mouse", "Ergonomic wireless mouse", 29.99, 150, "Accessories"),
                ("USB-C Hub", "7-in-1 USB-C hub adapter", 49.99, 80, "Accessories"),
                ("Gaming Keyboard", "Mechanical RGB keyboard", 89.99, 60, "Accessories"),
                ("4K Monitor", "27-inch 4K UHD monitor", 399.99, 40, "Electronics"),
            ]

            now = datetime.now().isoformat()
            for product in products:
                cursor.execute("""
                    INSERT INTO products (product_name, description, price, stock, category, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (*product, now))

        # Check if orders exist
        cursor.execute("SELECT COUNT(*) FROM orders")
        if cursor.fetchone()[0] == 0:
            # Add sample orders
            orders = [
                ("ORD-1001", "John Doe", "Laptop Pro 15", 1, 1299.99, "Shipped"),
                ("ORD-1002", "Jane Smith", "Wireless Mouse", 2, 29.99, "Processing"),
                ("ORD-1003", "Bob Johnson", "USB-C Hub", 1, 49.99, "Delivered"),
            ]

            now = datetime.now().isoformat()
            for order in orders:
                cursor.execute("""
                    INSERT INTO orders (order_number, customer_name, product_name, quantity, price, status, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (*order, now, now))

        conn.commit()
        conn.close()

    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results as list of dicts."""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(query, params)
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results

    def execute_update(self, query: str, params: tuple = ()) -> int:
        """Execute INSERT/UPDATE/DELETE and return affected rows."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        return affected

    def get_last_insert_id(self) -> int:
        """Get the last inserted row ID."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT last_insert_rowid()")
        last_id = cursor.fetchone()[0]
        conn.close()
        return last_id


# Initialize global database instance
db = EcommerceDB()