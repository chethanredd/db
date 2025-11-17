# user_profile.py
from flask import request, jsonify
from functools import wraps
import jwt
import bcrypt
import os
from mysql.connector import Error
import mysql.connector

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
            data = jwt.decode(token, os.getenv('JWT_SECRET', 'your-secret-key'), algorithms=['HS256'])
            current_user = data
        except:
            return jsonify({'error': 'Token is invalid'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated

def get_db_connection():
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', ''),
        'database': os.getenv('DB_NAME', 'shopscaledb'),
        'port': os.getenv('DB_PORT', 3306)
    }
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def create_user_profile_bp(app):
    from flask import Blueprint
    profile_bp = Blueprint('profile', __name__, url_prefix='/api/profile')
    
    # Get user profile
    @profile_bp.route('/', methods=['GET'])
    @token_required
    def get_profile(current_user):
        try:
            customer_id = current_user['customer_id']
            connection = get_db_connection()
            if not connection:
                return jsonify({'error': 'Database connection failed'}), 500
            
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT c.*, 
                       sa.street_address as ship_street, sa.city as ship_city, sa.state as ship_state, sa.postal_code as ship_postal,
                       ba.street_address as bill_street, ba.city as bill_city, ba.state as bill_state, ba.postal_code as bill_postal
                FROM customers c
                LEFT JOIN addresses sa ON c.shipping_address_id = sa.address_id
                LEFT JOIN addresses ba ON c.billing_address_id = ba.address_id
                WHERE c.customer_id = %s
            """, (customer_id,))
            
            profile = cursor.fetchone()
            
            if not profile:
                cursor.close()
                connection.close()
                return jsonify({'error': 'Profile not found'}), 404
            
            # Remove sensitive data
            if 'password_hash' in profile:
                del profile['password_hash']
            
            cursor.close()
            connection.close()
            
            return jsonify({'profile': profile})
        
        except Exception as e:
            print(f"Get profile error: {e}")
            return jsonify({'error': 'Failed to fetch profile'}), 500
    
    # Update user profile
    @profile_bp.route('/', methods=['PUT'])
    @token_required
    def update_profile(current_user):
        try:
            customer_id = current_user['customer_id']
            data = request.get_json()
            
            connection = get_db_connection()
            if not connection:
                return jsonify({'error': 'Database connection failed'}), 500
            
            cursor = connection.cursor()
            
            update_fields = []
            update_values = []
            
            if 'first_name' in data:
                update_fields.append('first_name = %s')
                update_values.append(data['first_name'])
            if 'last_name' in data:
                update_fields.append('last_name = %s')
                update_values.append(data['last_name'])
            if 'phone_number' in data:
                update_fields.append('phone_number = %s')
                update_values.append(data['phone_number'])
            if 'date_of_birth' in data:
                update_fields.append('date_of_birth = %s')
                update_values.append(data['date_of_birth'])
            if 'gender' in data:
                update_fields.append('gender = %s')
                update_values.append(data['gender'])
            
            if not update_fields:
                cursor.close()
                connection.close()
                return jsonify({'error': 'No fields to update'}), 400
            
            update_values.append(customer_id)
            update_query = f"UPDATE customers SET {', '.join(update_fields)} WHERE customer_id = %s"
            
            cursor.execute(update_query, update_values)
            connection.commit()
            cursor.close()
            connection.close()
            
            return jsonify({'message': 'Profile updated successfully'})
        
        except Exception as e:
            print(f"Update profile error: {e}")
            return jsonify({'error': 'Failed to update profile'}), 500
    
    # Change password
    @profile_bp.route('/change-password', methods=['POST'])
    @token_required
    def change_password(current_user):
        try:
            customer_id = current_user['customer_id']
            data = request.get_json()
            
            old_password = data.get('old_password')
            new_password = data.get('new_password')
            confirm_password = data.get('confirm_password')
            
            if not old_password or not new_password or not confirm_password:
                return jsonify({'error': 'All fields are required'}), 400
            
            if new_password != confirm_password:
                return jsonify({'error': 'Passwords do not match'}), 400
            
            if len(new_password) < 6:
                return jsonify({'error': 'Password must be at least 6 characters'}), 400
            
            connection = get_db_connection()
            if not connection:
                return jsonify({'error': 'Database connection failed'}), 500
            
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute("SELECT password_hash FROM customers WHERE customer_id = %s", (customer_id,))
            user = cursor.fetchone()
            
            if not user:
                cursor.close()
                connection.close()
                return jsonify({'error': 'User not found'}), 404
            
            # Verify old password
            stored_hash = user['password_hash']
            if isinstance(stored_hash, bytes):
                stored_hash = stored_hash.decode('utf-8')
            
            try:
                if not bcrypt.checkpw(old_password.encode('utf-8'), stored_hash.encode('utf-8')):
                    cursor.close()
                    connection.close()
                    return jsonify({'error': 'Current password is incorrect'}), 401
            except Exception as e:
                print(f"Password check error: {e}")
                cursor.close()
                connection.close()
                return jsonify({'error': 'Password verification failed'}), 500
            
            # Hash new password
            new_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            cursor.execute("""
                UPDATE customers SET password_hash = %s WHERE customer_id = %s
            """, (new_hash, customer_id))
            
            connection.commit()
            cursor.close()
            connection.close()
            
            return jsonify({'message': 'Password changed successfully'})
        
        except Exception as e:
            print(f"Change password error: {e}")
            return jsonify({'error': 'Failed to change password'}), 500
    
    # Get user statistics
    @profile_bp.route('/statistics', methods=['GET'])
    @token_required
    def get_statistics(current_user):
        try:
            customer_id = current_user['customer_id']
            connection = get_db_connection()
            if not connection:
                return jsonify({'error': 'Database connection failed'}), 500
            
            cursor = connection.cursor(dictionary=True)
            
            # Total orders
            cursor.execute("""
                SELECT COUNT(*) as count FROM orders WHERE customer_id = %s
            """, (customer_id,))
            total_orders = cursor.fetchone()['count']
            
            # Total spent
            cursor.execute("""
                SELECT COALESCE(SUM(total_amount), 0) as total 
                FROM orders 
                WHERE customer_id = %s AND order_status IN ('delivered', 'completed', 'confirmed', 'shipped')
            """, (customer_id,))
            total_spent = float(cursor.fetchone()['total'])
            
            # Total reviews
            cursor.execute("""
                SELECT COUNT(*) as count FROM reviews WHERE customer_id = %s
            """, (customer_id,))
            total_reviews = cursor.fetchone()['count']
            
            # Average rating
            cursor.execute("""
                SELECT COALESCE(AVG(rating), 0) as avg FROM reviews WHERE customer_id = %s
            """, (customer_id,))
            avg_rating = float(cursor.fetchone()['avg'])
            
            cursor.close()
            connection.close()
            
            return jsonify({
                'total_orders': total_orders,
                'total_spent': total_spent,
                'total_reviews': total_reviews,
                'average_rating': avg_rating
            })
        
        except Exception as e:
            print(f"Get statistics error: {e}")
            return jsonify({'error': 'Failed to fetch statistics'}), 500
    
    return profile_bp
