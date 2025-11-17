from flask import Blueprint, request, jsonify
import jwt
import bcrypt
from datetime import datetime, timedelta
from database import db_pool
import os

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    required_fields = ['email', 'password', 'first_name', 'last_name']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    email = data['email']
    password = data['password']
    first_name = data['first_name']
    last_name = data['last_name']
    phone_number = data.get('phone_number')

    # Check if user exists
    conn = db_pool.get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM customers WHERE email = %s", (email,))
    existing = cursor.fetchone()
    if existing:
        cursor.close()
        conn.close()
        return jsonify({"error": "Email already registered"}), 400

    # Hash password
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # Insert customer
    try:
        cursor.execute(
            "INSERT INTO customers (first_name, last_name, email, password_hash, phone_number) VALUES (%s, %s, %s, %s, %s)",
            (first_name, last_name, email, password_hash, phone_number)
        )
        customer_id = cursor.lastrowid

        # Create shopping cart for new customer
        cursor.execute("INSERT INTO shopping_cart (customer_id) VALUES (%s)", (customer_id,))

        conn.commit()

        # Generate JWT token
        token = jwt.encode({
            'customer_id': customer_id,
            'email': email,
            'exp': datetime.utcnow() + timedelta(days=7)
        }, os.getenv('JWT_SECRET', 'your-secret-key'), algorithm='HS256')

        cursor.close()
        conn.close()

        return jsonify({
            "message": "Registration successful",
            "token": token,
            "customer": {
                "customer_id": customer_id,
                "first_name": first_name,
                "last_name": last_name,
                "email": email
            }
        }), 201
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return jsonify({"error": "Registration failed"}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        print(f"Login attempt for: {email}")  # Debug log
        
        if not email or not password:
            return jsonify({"error": "Email and password required"}), 400

        conn = db_pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM customers WHERE email = %s", (email,))
        customer = cursor.fetchone()

        if not customer:
            print("Customer not found")  # Debug log
            cursor.close()
            conn.close()
            return jsonify({"error": "Invalid credentials"}), 401

        print(f"Found customer: {customer['email']}")  # Debug log
        print(f"Stored hash: {customer['password_hash']}")  # Debug log

        # Verify password with error handling
        try:
            valid_password = bcrypt.checkpw(password.encode('utf-8'), customer['password_hash'].encode('utf-8'))
            print(f"Password valid: {valid_password}")  # Debug log
        except Exception as e:
            print(f"Password check error: {e}")  # Debug log
            valid_password = False

        if not valid_password:
            cursor.close()
            conn.close()
            return jsonify({"error": "Invalid credentials"}), 401

        # Update last login
        cursor.execute("UPDATE customers SET last_login = NOW() WHERE customer_id = %s", (customer['customer_id'],))
        conn.commit()

        # Generate JWT token
        token = jwt.encode({
            'customer_id': customer['customer_id'],
            'email': customer['email'],
            'exp': datetime.utcnow() + timedelta(days=7)
        }, os.getenv('JWT_SECRET', 'your-secret-key'), algorithm='HS256')

        print(f"Login successful for: {email}, Token generated")  # Debug log

        cursor.close()
        conn.close()

        return jsonify({
            "message": "Login successful",
            "token": token,
            "customer": {
                "customer_id": customer['customer_id'],
                "first_name": customer['first_name'],
                "last_name": customer['last_name'],
                "email": customer['email']
            }
        })
    except Exception as e:
        print(f"Login error: {e}")  # Debug log
        return jsonify({"error": "Login failed"}), 500