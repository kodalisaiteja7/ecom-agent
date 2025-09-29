"""
Script to create and populate the database with sample data.
Run this to initialize the database before using the chat agent.
"""
from database import db
from datetime import datetime, timedelta
import random
import sys
import io

# Fix console encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def create_extended_sample_data():
    """Create comprehensive sample data for testing."""

    print("Initializing database...")

    # The database is already initialized with basic data in database.py
    # Let's add more comprehensive sample data

    # Additional products
    additional_products = [
        ("Bluetooth Headphones", "Noise-cancelling over-ear headphones", 149.99, 75, "Accessories"),
        ("External SSD 1TB", "Portable solid state drive", 119.99, 100, "Electronics"),
        ("Webcam HD Pro", "1080p webcam with auto-focus", 79.99, 45, "Electronics"),
        ("Ergonomic Chair", "Adjustable office chair with lumbar support", 299.99, 20, "Furniture"),
        ("Desk Lamp LED", "Adjustable LED desk lamp", 39.99, 90, "Accessories"),
        ("Phone Stand", "Aluminum adjustable phone stand", 24.99, 120, "Accessories"),
        ("Cable Organizer", "Desktop cable management system", 19.99, 200, "Accessories"),
        ("Laptop Sleeve 15", "Padded laptop sleeve", 29.99, 85, "Accessories"),
        ("USB Flash Drive 128GB", "High-speed USB 3.0 flash drive", 22.99, 150, "Electronics"),
        ("Smart Speaker", "Voice-activated smart speaker", 89.99, 55, "Electronics"),
    ]

    print("Adding additional products...")
    now = datetime.now().isoformat()

    for product in additional_products:
        try:
            db.execute_update("""
                INSERT OR IGNORE INTO products (product_name, description, price, stock, category, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (*product, now))
        except Exception as e:
            print(f"   Warning: Product '{product[0]}' may already exist: {e}")

    # Additional orders with varied statuses
    additional_orders = [
        ("ORD-1004", "Sarah Williams", "Bluetooth Headphones", 1, 149.99, "Shipped"),
        ("ORD-1005", "Michael Chen", "4K Monitor", 1, 399.99, "Processing"),
        ("ORD-1006", "Emily Davis", "External SSD 1TB", 2, 119.99, "Delivered"),
        ("ORD-1007", "David Martinez", "Webcam HD Pro", 1, 79.99, "Processing"),
        ("ORD-1008", "Lisa Anderson", "Ergonomic Chair", 1, 299.99, "Shipped"),
        ("ORD-1009", "James Wilson", "Desk Lamp LED", 3, 39.99, "Delivered"),
        ("ORD-1010", "Jessica Taylor", "USB-C Hub", 2, 49.99, "Processing"),
        ("ORD-1011", "Robert Brown", "Gaming Keyboard", 1, 89.99, "Shipped"),
        ("ORD-1012", "Amanda Garcia", "Smart Speaker", 1, 89.99, "Processing"),
        ("ORD-1013", "Christopher Lee", "Laptop Sleeve 15", 2, 29.99, "Delivered"),
    ]

    print("Adding additional orders...")

    # Create orders with varied timestamps
    base_date = datetime.now()

    for i, order in enumerate(additional_orders):
        # Vary the creation date
        order_date = (base_date - timedelta(days=random.randint(0, 14))).isoformat()

        try:
            db.execute_update("""
                INSERT OR IGNORE INTO orders (order_number, customer_name, product_name, quantity, price, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (*order, order_date, order_date))
        except Exception as e:
            print(f"   Warning: Order '{order[0]}' may already exist: {e}")

    # Display summary
    print("\n" + "=" * 70)
    print("SAMPLE DATA CREATED SUCCESSFULLY!")
    print("=" * 70)

    # Count records
    product_count = db.execute_query("SELECT COUNT(*) as count FROM products")[0]['count']
    order_count = db.execute_query("SELECT COUNT(*) as count FROM orders")[0]['count']

    print(f"\nDatabase Summary:")
    print(f"   * Total Products: {product_count}")
    print(f"   * Total Orders: {order_count}")

    # Show product categories
    categories = db.execute_query("""
        SELECT category, COUNT(*) as count, SUM(stock) as total_stock
        FROM products
        GROUP BY category
        ORDER BY count DESC
    """)

    print(f"\nProducts by Category:")
    for cat in categories:
        print(f"   * {cat['category']}: {cat['count']} products ({cat['total_stock']} units in stock)")

    # Show order statuses
    statuses = db.execute_query("""
        SELECT status, COUNT(*) as count
        FROM orders
        GROUP BY status
        ORDER BY count DESC
    """)

    print(f"\nOrders by Status:")
    for status in statuses:
        print(f"   * {status['status']}: {status['count']} orders")

    # Show sample products
    print(f"\nSample Products:")
    sample_products = db.execute_query("SELECT product_name, price, stock, category FROM products LIMIT 5")
    for p in sample_products:
        print(f"   * {p['product_name']:<25} ${p['price']:<8} | Stock: {p['stock']:<4} | {p['category']}")

    # Show sample orders
    print(f"\nSample Orders:")
    sample_orders = db.execute_query("SELECT order_number, customer_name, product_name, status FROM orders LIMIT 5")
    for o in sample_orders:
        print(f"   * {o['order_number']}: {o['customer_name']:<20} | {o['product_name']:<25} | {o['status']}")

    print("\n" + "=" * 70)
    print("You can now run: python chat_interface.py")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    try:
        create_extended_sample_data()
    except Exception as e:
        print(f"\nError creating sample data: {e}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")