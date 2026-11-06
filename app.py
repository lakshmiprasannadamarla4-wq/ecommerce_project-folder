from flask import Flask, jsonify, request, render_template
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS products
                 (id INTEGER PRIMARY KEY, name TEXT, price REAL, image TEXT, category TEXT, stock INTEGER)""")
    c.execute("""CREATE TABLE IF NOT EXISTS orders
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, user TEXT, product TEXT, qty INTEGER, total REAL, status TEXT)""")
    c.execute("SELECT COUNT(*) FROM products")
    if c.fetchone()[0]==0:
        products = [
            (1, "Wireless Headphones", 1999, "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400", "Electronics", 20),
            (2, "Smart Watch", 2999, "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400", "Electronics", 15),
            (3, "Running Shoes", 1499, "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400", "Fashion", 30),
            (4, "T-Shirt", 499, "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400", "Fashion", 50),
            (5, "Backpack", 899, "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=400", "Fashion", 25),
            (6, "Coffee Maker", 2499, "https://images.unsplash.com/photo-1517668808822-9ebb02f2a0e6?w=400", "Home", 10),
            (7, "Sunglasses", 799, "https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=400", "Fashion", 40),
            (8, "Laptop Stand", 999, "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=400", "Electronics", 18),
        ]
        c.executemany("INSERT INTO products VALUES (?,?,?,?,?,?)", products)
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    return render_template('index.html')

# API - Get Products
@app.route('/api/products')
def get_products():
    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()
    c.execute("SELECT * FROM products")
    rows = c.fetchall()
    conn.close()
    return jsonify([{"id":r[0],"name":r[1],"price":r[2],"image":r[3],"category":r[4],"stock":r[5]} for r in rows])

# API - Add Product (Admin only)
@app.route('/api/products', methods=['POST'])
def add_product():
    data = request.json
    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()
    c.execute("INSERT INTO products (name, price, image, category, stock) VALUES (?,?,?,?,?)",
              (data['name'], data['price'], data.get('image',''), data.get('category','General'), data.get('stock',10)))
    conn.commit()
    conn.close()
    return jsonify({"message":"Product added successfully"})

# API - Get Orders
@app.route('/api/orders')
def get_orders():
    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()
    c.execute("SELECT * FROM orders")
    rows = c.fetchall()
    conn.close()
    return jsonify([{"id":r[0],"user":r[1],"product":r[2],"qty":r[3],"total":r[4],"status":r[5]} for r in rows])

# API - Create Order
@app.route('/api/orders', methods=['POST'])
def create_order():
    data = request.json
    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()
    c.execute("INSERT INTO orders (user, product, qty, total, status) VALUES (?,?,?,?,?)",
              (data.get('user','Guest'), data['product'], data['qty'], data['total'], "Ordered"))
    conn.commit()
    order_id = c.lastrowid
    conn.close()
    return jsonify({"message":"Order placed","order_id":order_id, "status":"Ordered"})

# API - Update Order Status
@app.route('/api/orders/<int:order_id>', methods=['PUT'])
def update_order(order_id):
    data = request.json
    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()
    c.execute("UPDATE orders SET status=? WHERE id=?", (data['status'], order_id))
    conn.commit()
    conn.close()
    return jsonify({"message":"Order status updated"})

# LOGIN - Role Based
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    if data.get('username')=="admin" and data.get('password')=="admin123":
        return jsonify({"role":"admin","message":"Admin login success"})
    elif data.get('username')=="user" and data.get('password')=="user123":
        return jsonify({"role":"user","message":"User login success"})
    else:
        return jsonify({"error":"Invalid credentials"}), 401

if __name__ == '__main__':
    app.run(debug=True, port=5000)
