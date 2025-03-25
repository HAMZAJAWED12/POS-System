import sqlite3
from fpdf import FPDF
import datetime
import os
import platform
import sys

# ✅ Save outside the bundled .exe
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)  # The folder where .exe is located
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(BASE_DIR, "pos.db")

# ------------------- Table Creation -------------------
def create_tables():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cart (
            product_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            quantity INTEGER NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            total_price REAL NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_name TEXT NOT NULL,
            price REAL NOT NULL,
            quantity INTEGER NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id)
        )
    ''')

    conn.commit()
    conn.close()


# ------------------- Products -------------------
def add_product(name, price, stock):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO products (name, price, stock) VALUES (?, ?, ?)", (name, price, stock))
    conn.commit()
    conn.close()

def get_products():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    conn.close()
    return products

def update_product(product_id, name, price, stock):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET name=?, price=?, stock=? WHERE id=?", (name, price, stock, product_id))
    conn.commit()
    conn.close()

def delete_product(product_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id=?", (product_id,))
    conn.commit()
    conn.close()

# ------------------- Cart -------------------
def get_cart_items():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT product_id, name, price, quantity FROM cart")
    items = cursor.fetchall()
    conn.close()
    return items

def add_to_cart(product_id, name, price):
    if not product_id or not name or not price:
        print("❌ Error: Invalid product details")
        return False

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT quantity FROM cart WHERE product_id = ?", (product_id,))
        row = cursor.fetchone()

        if row:
            cursor.execute("UPDATE cart SET quantity = quantity + 1 WHERE product_id = ?", (product_id,))
        else:
            cursor.execute("INSERT INTO cart (product_id, name, price, quantity) VALUES (?, ?, ?, 1)",
                           (product_id, name, price))
        conn.commit()
        return True
    except Exception as e:
        print(f"❌ Database Error: {e}")
        return False
    finally:
        conn.close()

def update_cart_quantity(product_id, increase=True):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if increase:
        cursor.execute("UPDATE cart SET quantity = quantity + 1 WHERE product_id = ?", (product_id,))
    else:
        cursor.execute("UPDATE cart SET quantity = quantity - 1 WHERE product_id = ? AND quantity > 1", (product_id,))
    conn.commit()
    conn.close()

def remove_from_cart(product_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cart WHERE product_id = ?", (product_id,))
    conn.commit()
    conn.close()

def clear_cart():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cart")
    conn.commit()
    conn.close()

# ------------------- Orders -------------------
def save_order():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name, price, quantity FROM cart")
    cart_items = cursor.fetchall()

    if not cart_items:
        print("❌ Error: No items in the cart to process an order.")
        return None

    total_price = sum(item[1] * item[2] for item in cart_items)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("INSERT INTO orders (timestamp, total_price) VALUES (?, ?)", (timestamp, total_price))
    order_id = cursor.lastrowid

    for name, price, quantity in cart_items:
        cursor.execute("INSERT INTO order_items (order_id, product_name, price, quantity) VALUES (?, ?, ?, ?)",
                       (order_id, name, price, quantity))

    cursor.execute("DELETE FROM cart")
    conn.commit()
    conn.close()

    generate_invoice(order_id, timestamp, cart_items, total_price)
    return order_id

def generate_invoice(order_id, timestamp, items, total_price):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "INVOICE", ln=True, align="C")
    pdf.ln(10)

    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, f"Order ID: {order_id}", ln=True)
    pdf.cell(200, 10, f"Date: {timestamp}", ln=True)
    pdf.ln(10)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(80, 10, "Product", 1)
    pdf.cell(40, 10, "Price", 1)
    pdf.cell(40, 10, "Quantity", 1)
    pdf.cell(40, 10, "Total", 1)
    pdf.ln()

    pdf.set_font("Arial", size=12)
    for name, price, quantity in items:
        pdf.cell(80, 10, name, 1)
        pdf.cell(40, 10, f"${price:.2f}", 1)
        pdf.cell(40, 10, str(quantity), 1)
        pdf.cell(40, 10, f"${price * quantity:.2f}", 1)
        pdf.ln()

    pdf.cell(160, 10, "TOTAL:", 1)
    pdf.cell(40, 10, f"${total_price:.2f}", 1)
    pdf.ln(10)

    # ✅ ADDING WATERMARK: "Developed by Hamza Jawed"
    pdf.set_font("Arial", "I", 10)  # Italic font for watermark
    pdf.set_text_color(100, 100, 100)  # Gray color for watermark
    pdf.cell(200, 10, "Developed by Hamza Jawed", ln=True, align="C")  # Centered text
    pdf.set_text_color(0, 0, 0)  # Reset text color

    filename = f"invoice_{order_id}.pdf"
    pdf.output(filename)
    print(f"✅ Invoice generated: {filename}")

def get_all_orders():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, timestamp, total_price FROM orders ORDER BY timestamp DESC")
    orders = cursor.fetchall()
    conn.close()
    return orders

def regenerate_invoice(order_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, total_price FROM orders WHERE id = ?", (order_id,))
    order = cursor.fetchone()

    if not order:
        print("❌ Order not found!")
        return

    timestamp, total = order
    cursor.execute("SELECT product_name, price, quantity FROM order_items WHERE order_id = ?", (order_id,))
    items = cursor.fetchall()
    conn.close()

    generate_invoice(order_id, timestamp, items, total)

def get_dashboard_stats():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM products")
    total_products = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM orders")
    total_orders = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(total_price) FROM orders")
    total_revenue = cursor.fetchone()[0] or 0.0

    conn.close()
    return {
        "products": total_products,
        "orders": total_orders,
        "revenue": total_revenue
    }

def get_total_products():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM products")
    result = cursor.fetchone()[0]
    conn.close()
    return result

def get_total_orders():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM orders")
    result = cursor.fetchone()[0]
    conn.close()
    return result

def get_total_revenue():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(total_price) FROM orders")
    result = cursor.fetchone()[0]
    conn.close()
    return result if result else 0.0

def print_invoice(order_id):
    filename = f"invoice_{order_id}.pdf"
    if platform.system() == "Windows":
        try:
            print(f"🖨️ Sending {filename} to default printer...")
            os.startfile(filename, "print")
        except Exception as e:
            print(f"❌ Failed to print: {e}")
    else:
        print("🚫 Printing is only supported on Windows right now.")

def get_sales_data(group_by='date'):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if group_by == 'date':
        cursor.execute("""
            SELECT DATE(timestamp), SUM(total_price)
            FROM orders
            GROUP BY DATE(timestamp)
            ORDER BY DATE(timestamp) DESC
            LIMIT 7
        """)
    elif group_by == 'product':
        cursor.execute("""
            SELECT product_name, SUM(quantity)
            FROM order_items
            GROUP BY product_name
            ORDER BY SUM(quantity) DESC
            LIMIT 5
        """)
    else:
        return []

    data = cursor.fetchall()
    conn.close()
    return data
