# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
import bcrypt
import jwt
import datetime
from functools import wraps
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('JWT_SECRET', 'your-secret-key')

# Configure CORS properly for all origins and methods
CORS(app, 
     resources={r"/api/*": {
         "origins": ["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000", "http://127.0.0.1:5173"],
         "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         "allow_headers": ["Content-Type", "Authorization"],
         "expose_headers": ["Content-Type"],
         "supports_credentials": True,
         "max_age": 3600
     }}
)

# Import and register blueprints after app creation to avoid circular imports
from admin_routes import create_admin_bp
from orders import create_orders_bp
from addresses import create_addresses_bp
from reviews import create_reviews_bp
from user_profile import create_user_profile_bp
from payments import create_payments_bp

admin_bp = create_admin_bp(app)
orders_bp = create_orders_bp(app)
addresses_bp = create_addresses_bp(app)
reviews_bp = create_reviews_bp(app)
profile_bp = create_user_profile_bp(app)
payments_bp = create_payments_bp(app)

app.register_blueprint(admin_bp)
app.register_blueprint(orders_bp)
app.register_blueprint(addresses_bp)
app.register_blueprint(reviews_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(payments_bp)

# Database configuration
db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'shopscaledb'),
    'port': os.getenv('DB_PORT', 3306)
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = data
        except:
            return jsonify({'error': 'Token is invalid'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated

# Authentication Routes
@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        required_fields = ['email', 'password', 'first_name', 'last_name']
        
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        email = data['email']
        password = data['password']
        first_name = data['first_name']
        last_name = data['last_name']
        phone_number = data.get('phone_number')
        
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor(dictionary=True)
        
        # Check if user exists
        cursor.execute("SELECT * FROM customers WHERE email = %s", (email,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            cursor.close()
            connection.close()
            return jsonify({'error': 'Email already registered'}), 400
        
        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Insert customer
        cursor.execute(
            "INSERT INTO customers (first_name, last_name, email, password_hash, phone_number) VALUES (%s, %s, %s, %s, %s)",
            (first_name, last_name, email, hashed_password, phone_number)
        )
        customer_id = cursor.lastrowid
        
        # Create shopping cart
        cursor.execute("INSERT INTO shopping_cart (customer_id) VALUES (%s)", (customer_id,))
        
        connection.commit()
        
        # Generate JWT token
        token = jwt.encode({
            'customer_id': customer_id,
            'email': email,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'message': 'Registration successful',
            'token': token,
            'customer': {
                'customer_id': customer_id,
                'first_name': first_name,
                'last_name': last_name,
                'email': email
            }
        }), 201
        
    except Exception as e:
        print(f"Registration error: {e}")
        return jsonify({'error': 'Registration failed'}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        print(f"Login attempt for: {email}")

        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400

        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500

        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM customers WHERE email = %s", (email,))
        customer = cursor.fetchone()

        if not customer:
            cursor.close()
            connection.close()
            return jsonify({'error': 'Invalid credentials'}), 401

        # Debug: Print what we're comparing
        print(f"Input password: {password}")
        print(f"Stored hash: {customer['password_hash']}")
        
        # Verify password - handle both string and bytes
        try:
            # Ensure the stored hash is in string format
            stored_hash = customer['password_hash']
            if isinstance(stored_hash, bytes):
                stored_hash = stored_hash.decode('utf-8')
                
            valid_password = bcrypt.checkpw(
                password.encode('utf-8'), 
                stored_hash.encode('utf-8')
            )
            print(f"Password valid: {valid_password}")
        except Exception as e:
            print(f"Password verification error: {e}")
            valid_password = False

        if not valid_password:
            cursor.close()
            connection.close()
            return jsonify({'error': 'Invalid credentials'}), 401

        # Update last login
        cursor.execute("UPDATE customers SET last_login = NOW() WHERE customer_id = %s", (customer['customer_id'],))
        connection.commit()

        # Generate JWT token
        token = jwt.encode({
            'customer_id': customer['customer_id'],
            'email': customer['email'],
            'is_admin': customer['email'] == 'admin@shopscale.com',  # Simple admin check
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
        }, app.config['SECRET_KEY'], algorithm='HS256')

        cursor.close()
        connection.close()

        return jsonify({
            'message': 'Login successful',
            'token': token,
            'customer': {
                'customer_id': customer['customer_id'],
                'first_name': customer['first_name'],
                'last_name': customer['last_name'],
                'email': customer['email'],
                'is_admin': customer['email'] == 'admin@shopscale.com'
            }
        })

    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({'error': 'Login failed'}), 500

# Products Routes
@app.route('/api/products', methods=['GET'])
def get_products():
    try:
        category = request.args.get('category', 'all')
        search = request.args.get('search', '')
        featured = request.args.get('featured', '')
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor(dictionary=True)
        
        query = """
            SELECT 
                p.product_id as id,
                p.product_name as name,
                p.description,
                p.price,
                p.stock_quantity as stock,
                p.sku,
                p.brand,
                p.featured,
                p.image,
                GROUP_CONCAT(DISTINCT c.category_name) as categories,
                COALESCE(AVG(r.rating), 0) as rating,
                COUNT(DISTINCT r.review_id) as reviews
            FROM products p
            LEFT JOIN product_categories pc ON p.product_id = pc.product_id
            LEFT JOIN categories c ON pc.category_id = c.category_id
            LEFT JOIN reviews r ON p.product_id = r.product_id
            WHERE p.is_active = TRUE
        """
        
        params = []
        
        if category and category != 'all':
            query += " AND c.category_name = %s"
            params.append(category)
        
        if search:
            query += " AND (p.product_name LIKE %s OR p.description LIKE %s)"
            params.extend([f"%{search}%", f"%{search}%"])
        
        if featured.lower() == 'true':
            query += " AND p.featured = TRUE"
        
        query += " GROUP BY p.product_id ORDER BY p.created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        products = cursor.fetchall()
        
        # Format products for frontend
        formatted_products = []
        for product in products:
            formatted_product = {
                'id': product['id'],
                'name': product['name'],
                'description': product['description'],
                'price': float(product['price']),
                'image': product['image'] or 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400',  # Default image
                'category': product['categories'].split(',')[0] if product['categories'] else 'Uncategorized',
                'brand': product['brand'],
                'rating': round(float(product['rating'])),
                'reviews': product['reviews'],
                'stock': product['stock'],
                'featured': bool(product['featured'])
            }
            formatted_products.append(formatted_product)
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'products': formatted_products,
            'count': len(formatted_products)
        })
        
    except Exception as e:
        print(f"Get products error: {e}")
        return jsonify({'error': 'Failed to fetch products'}), 500

@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT 
                p.product_id as id,
                p.product_name as name,
                p.description,
                p.price,
                p.stock_quantity as stock,
                p.sku,
                p.brand,
                p.featured,
                p.image,
                p.weight,
                p.color,
                p.size,
                GROUP_CONCAT(DISTINCT c.category_name) as categories,
                COALESCE(AVG(r.rating), 0) as rating,
                COUNT(DISTINCT r.review_id) as reviews
            FROM products p
            LEFT JOIN product_categories pc ON p.product_id = pc.product_id
            LEFT JOIN categories c ON pc.category_id = c.category_id
            LEFT JOIN reviews r ON p.product_id = r.product_id
            WHERE p.product_id = %s AND p.is_active = TRUE
            GROUP BY p.product_id
        """, (product_id,))
        
        product = cursor.fetchone()
        
        if not product:
            cursor.close()
            connection.close()
            return jsonify({'error': 'Product not found'}), 404
        
        formatted_product = {
            'id': product['id'],
            'name': product['name'],
            'description': product['description'],
            'price': float(product['price']),
            'image': product['image'] or 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400',
            'category': product['categories'].split(',')[0] if product['categories'] else 'Uncategorized',
            'brand': product['brand'],
            'rating': round(float(product['rating'])),
            'reviews': product['reviews'],
            'stock': product['stock'],
            'featured': bool(product['featured']),
            'weight': product['weight'],
            'color': product['color'],
            'size': product['size']
        }
        
        cursor.close()
        connection.close()
        
        return jsonify(formatted_product)
        
    except Exception as e:
        print(f"Get product error: {e}")
        return jsonify({'error': 'Failed to fetch product'}), 500

# Cart Routes
@app.route('/api/cart', methods=['GET'])
@token_required
def get_cart(current_user):
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor(dictionary=True)
        
        # Get customer's cart
        cursor.execute("SELECT cart_id FROM shopping_cart WHERE customer_id = %s", (current_user['customer_id'],))
        cart = cursor.fetchone()
        
        if not cart:
            return jsonify({'items': [], 'total': 0, 'item_count': 0})
        
        # Get cart items
        cursor.execute("""
            SELECT 
                ci.cart_item_id,
                ci.product_id,
                ci.quantity,
                p.product_name as name,
                p.price,
                p.image,
                p.stock_quantity as stock
            FROM cart_items ci
            JOIN products p ON ci.product_id = p.product_id
            WHERE ci.cart_id = %s
        """, (cart['cart_id'],))
        
        items = cursor.fetchall()
        
        formatted_items = []
        for item in items:
            formatted_item = {
                'id': item['product_id'],
                'cart_item_id': item['cart_item_id'],
                'name': item['name'],
                'price': float(item['price']),
                'image': item['image'] or 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400',
                'quantity': item['quantity'],
                'stock': item['stock']
            }
            formatted_items.append(formatted_item)
        
        total = sum(item['price'] * item['quantity'] for item in formatted_items)
        item_count = sum(item['quantity'] for item in formatted_items)
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'items': formatted_items,
            'total': total,
            'item_count': item_count
        })
        
    except Exception as e:
        print(f"Get cart error: {e}")
        return jsonify({'error': 'Failed to fetch cart'}), 500

@app.route('/api/cart/items', methods=['POST'])
@token_required
def add_to_cart(current_user):
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)
        
        if not product_id:
            return jsonify({'error': 'Product ID is required'}), 400
        
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor(dictionary=True)
        
        # Get or create cart
        cursor.execute("SELECT cart_id FROM shopping_cart WHERE customer_id = %s", (current_user['customer_id'],))
        cart = cursor.fetchone()
        
        if not cart:
            cursor.execute("INSERT INTO shopping_cart (customer_id) VALUES (%s)", (current_user['customer_id'],))
            cart_id = cursor.lastrowid
        else:
            cart_id = cart['cart_id']
        
        # Check if item already in cart
        cursor.execute("SELECT * FROM cart_items WHERE cart_id = %s AND product_id = %s", (cart_id, product_id))
        existing_item = cursor.fetchone()
        
        if existing_item:
            # Update quantity
            cursor.execute(
                "UPDATE cart_items SET quantity = quantity + %s WHERE cart_item_id = %s",
                (quantity, existing_item['cart_item_id'])
            )
        else:
            # Add new item
            cursor.execute(
                "INSERT INTO cart_items (cart_id, product_id, quantity) VALUES (%s, %s, %s)",
                (cart_id, product_id, quantity)
            )
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({'message': 'Item added to cart successfully'})
        
    except Exception as e:
        print(f"Add to cart error: {e}")
        return jsonify({'error': 'Failed to add item to cart'}), 500

@app.route('/api/cart/items/<int:item_id>', methods=['PUT'])
@token_required
def update_cart_item(current_user, item_id):
    try:
        data = request.get_json()
        quantity = data.get('quantity')
        
        if quantity < 1:
            return jsonify({'error': 'Quantity must be at least 1'}), 400
        
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor()
        
        cursor.execute("""
            UPDATE cart_items 
            SET quantity = %s 
            WHERE cart_item_id = %s 
            AND cart_id IN (SELECT cart_id FROM shopping_cart WHERE customer_id = %s)
        """, (quantity, item_id, current_user['customer_id']))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({'message': 'Cart item updated successfully'})
        
    except Exception as e:
        print(f"Update cart error: {e}")
        return jsonify({'error': 'Failed to update cart item'}), 500

@app.route('/api/cart/items/<int:item_id>', methods=['DELETE'])
@token_required
def remove_cart_item(current_user, item_id):
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor()
        
        cursor.execute("""
            DELETE FROM cart_items 
            WHERE cart_item_id = %s 
            AND cart_id IN (SELECT cart_id FROM shopping_cart WHERE customer_id = %s)
        """, (item_id, current_user['customer_id']))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({'message': 'Item removed from cart successfully'})
        
    except Exception as e:
        print(f"Remove from cart error: {e}")
        return jsonify({'error': 'Failed to remove item from cart'}), 500

# Health check
@app.route('/api/health', methods=['GET'])
def health_check():
    try:
        connection = get_db_connection()
        if connection:
            connection.close()
            return jsonify({
                'status': 'OK',
                'message': 'ShopScale API is running',
                'database': 'Connected'
            })
        else:
            return jsonify({
                'status': 'ERROR',
                'message': 'Database connection failed'
            }), 500
    except Exception as e:
        return jsonify({
            'status': 'ERROR',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)