from flask import Flask, jsonify, render_template_string
from redis import Redis
import json

app = Flask(__name__)
redis = Redis(host="redis", port=6379)

RESTAURANTS = [
    {"id": 1, "name": "Pizza Palace", "cuisine": "Italian", "rating": 4.5, "time": "30 mins", "emoji": "🍕"},
    {"id": 2, "name": "Burger King", "cuisine": "American", "rating": 4.2, "time": "25 mins", "emoji": "🍔"},
    {"id": 3, "name": "Biryani House", "cuisine": "Indian", "rating": 4.8, "time": "40 mins", "emoji": "🍛"},
    {"id": 4, "name": "Sushi World", "cuisine": "Japanese", "rating": 4.6, "time": "35 mins", "emoji": "🍣"},
    {"id": 5, "name": "Taco Fiesta", "cuisine": "Mexican", "rating": 4.3, "time": "20 mins", "emoji": "🌮"},
    {"id": 6, "name": "Chinese Dragon", "cuisine": "Chinese", "rating": 4.4, "time": "30 mins", "emoji": "🍜"},
]

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>FoodRunner 🍕</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background: #f8f9fa; font-family: Arial; }
        .navbar { background: #ff6b35 !important; }
        .card { border-radius: 15px; transition: transform 0.2s; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .card:hover { transform: translateY(-5px); }
        .btn-order { background: #ff6b35; color: white; border: none; border-radius: 20px; padding: 8px 20px; }
        .btn-order:hover { background: #e55a2b; color: white; }
        .rating { color: #ffc107; }
        .hero { background: linear-gradient(135deg, #ff6b35, #f7931e); color: white; padding: 60px 0; }
        .source-badge { font-size: 10px; }
    </style>
</head>
<body>
    <nav class="navbar navbar-dark">
        <div class="container">
            <a class="navbar-brand fw-bold fs-3" href="/">🍕 FoodRunner</a>
            <a href="/orders" class="btn btn-light">📋 My Orders</a>
        </div>
    </nav>

    <div class="hero text-center mb-5">
        <h1 class="display-4 fw-bold">Hungry? We got you! 🚀</h1>
        <p class="lead">Order from the best restaurants near you</p>
        <span class="badge bg-light text-dark source-badge">Data from: {{ data_source }}</span>
    </div>

    <div class="container">
        <h3 class="mb-4">🏪 Restaurants near you</h3>
        <div class="row">
            {% for r in restaurants %}
            <div class="col-md-4 mb-4">
                <div class="card p-3">
                    <div class="text-center display-1">{{ r.emoji }}</div>
                    <div class="card-body text-center">
                        <h5 class="fw-bold">{{ r.name }}</h5>
                        <p class="text-muted">{{ r.cuisine }}</p>
                        <p class="rating">⭐ {{ r.rating }}</p>
                        <p>🕐 {{ r.time }}</p>
                        <a href="/order/{{ r.id }}" class="btn btn-order">Order Now</a>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
"""

ORDER_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Order from {{ restaurant.name }}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background: #f8f9fa; }
        .navbar { background: #ff6b35 !important; }
        .btn-order { background: #ff6b35; color: white; border: none; border-radius: 20px; padding: 10px 30px; }
        .card { border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
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
                <div class="card p-4">
                    <div class="text-center display-1">{{ restaurant.emoji }}</div>
                    <h3 class="text-center fw-bold">{{ restaurant.name }}</h3>
                    <p class="text-center text-muted">⭐ {{ restaurant.rating }} | 🕐 {{ restaurant.time }}</p>
                    <hr>
                    <form action="http://localhost:8081/place-order" method="POST">
                        <input type="hidden" name="restaurant_id" value="{{ restaurant.id }}">
                        <input type="hidden" name="restaurant_name" value="{{ restaurant.name }}">
                        <div class="mb-3">
                            <label class="form-label fw-bold">Your Name</label>
                            <input type="text" name="customer_name" class="form-control" placeholder="Enter your name" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label fw-bold">Your Address</label>
                            <input type="text" name="address" class="form-control" placeholder="Enter delivery address" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label fw-bold">What do you want?</label>
                            <textarea name="items" class="form-control" placeholder="e.g. 2 Pizzas, 1 Coke" required></textarea>
                        </div>
                        <button type="submit" class="btn btn-order w-100 fw-bold">Place Order 🚀</button>
                    </form>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

@app.route("/")
def home():
    cached = redis.get("restaurants")
    if cached:
        restaurants = json.loads(cached)
        source = "cache 🚀"
    else:
        restaurants = RESTAURANTS
        redis.set("restaurants", json.dumps(restaurants), ex=300)
        source = "database 🗄️"
    return render_template_string(HTML, restaurants=restaurants, data_source=source)

@app.route("/order/<int:restaurant_id>")
def order_page(restaurant_id):
    restaurant = next((r for r in RESTAURANTS if r["id"] == restaurant_id), None)
    if not restaurant:
        return "Restaurant not found!", 404
    return render_template_string(ORDER_HTML, restaurant=restaurant)

@app.route("/api/restaurants")
def api_restaurants():
    return jsonify(RESTAURANTS)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
