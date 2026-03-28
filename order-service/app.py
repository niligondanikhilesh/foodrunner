from flask import Flask, request, render_template_string
import psycopg2
import os
import uuid
import time

app = Flask(__name__)

def get_db():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "postgres"),
        database=os.environ.get("DB_NAME", "foodrunner"),
        user=os.environ.get("DB_USER", "admin"),
        password=os.environ.get("DB_PASSWORD", "password")
    )

def init_db():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id VARCHAR(50) PRIMARY KEY,
                customer_name VARCHAR(100),
                restaurant_name VARCHAR(100),
                items TEXT,
                address TEXT,
                status VARCHAR(50),
                created_at FLOAT
            );
        """)
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"DB init error: {e}")

SUCCESS_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Order Placed!</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background: #f8f9fa; }
        .navbar { background: #ff6b35 !important; }
        .card { border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .status { background: #ff6b35; color: white; border-radius: 20px; padding: 5px 15px; }
    </style>
</head>
<body>
    <nav class="navbar navbar-dark">
        <div class="container">
            <a class="navbar-brand fw-bold fs-3" href="/">🍕 FoodRunner</a>
        </div>
    </nav>

    <div class="container mt-5">
        <div class="row justify-content-center">
            <div class="col-md-6">
                <div class="card p-4 text-center">
                    <div class="display-1">🎉</div>
                    <h3 class="fw-bold text-success">Order Placed Successfully!</h3>
                    <hr>
                    <p><strong>Order ID:</strong> {{ order_id }}</p>
                    <p><strong>Customer:</strong> {{ customer_name }}</p>
                    <p><strong>Restaurant:</strong> {{ restaurant_name }}</p>
                    <p><strong>Items:</strong> {{ items }}</p>
                    <p><strong>Address:</strong> {{ address }}</p>
                    <p><strong>Status:</strong> <span class="status">{{ status }}</span></p>
                    <hr>
                    <a href="/orders" class="btn btn-warning fw-bold">📋 Track My Orders</a>
                    <a href="/" class="btn btn-outline-secondary mt-2">🏠 Back to Home</a>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

ORDERS_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>My Orders</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background: #f8f9fa; }
        .navbar { background: #ff6b35 !important; }
        .card { border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .status { background: #ff6b35; color: white; border-radius: 20px; padding: 3px 10px; font-size: 12px; }
    </style>
</head>
<body>
    <nav class="navbar navbar-dark">
        <div class="container">
            <a class="navbar-brand fw-bold fs-3" href="/">🍕 FoodRunner</a>
        </div>
    </nav>

    <div class="container mt-5">
        <h3 class="mb-4">📋 All Orders</h3>
        {% if orders %}
        <div class="row">
            {% for order in orders %}
            <div class="col-md-6 mb-3">
                <div class="card p-3">
                    <h5 class="fw-bold">{{ order[4] }} 🍕</h5>
                    <p><strong>Customer:</strong> {{ order[1] }}</p>
                    <p><strong>Restaurant:</strong> {{ order[2] }}</p>
                    <p><strong>Items:</strong> {{ order[3] }}</p>
                    <p><strong>Address:</strong> {{ order[4] }}</p>
                    <span class="status">{{ order[5] }}</span>
                </div>
            </div>
            {% endfor %}
        </div>
        {% else %}
        <div class="text-center mt-5">
            <div class="display-1">🛒</div>
            <h4>No orders yet!</h4>
            <a href="/" class="btn btn-warning mt-3">Order Now</a>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route("/place-order", methods=["POST"])
def place_order():
    init_db()
    order_id = str(uuid.uuid4())[:8].upper()
    customer_name = request.form.get("customer_name")
    restaurant_name = request.form.get("restaurant_name")
    items = request.form.get("items")
    address = request.form.get("address")
    status = "Order Confirmed! 🎉"

    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO orders (id, customer_name, restaurant_name, items, address, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (order_id, customer_name, restaurant_name, items, address, status, time.time()))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

    return render_template_string(SUCCESS_HTML,
        order_id=order_id,
        customer_name=customer_name,
        restaurant_name=restaurant_name,
        items=items,
        address=address,
        status=status
    )

@app.route("/orders")
def orders():
    init_db()
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM orders ORDER BY created_at DESC;")
        all_orders = cur.fetchall()
        conn.close()
    except:
        all_orders = []
    return render_template_string(ORDERS_HTML, orders=all_orders)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
