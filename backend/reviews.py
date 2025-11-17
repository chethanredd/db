# reviews.py
from flask import request, jsonify
from functools import wraps
import jwt
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

def create_reviews_bp(app):
    from flask import Blueprint
    reviews_bp = Blueprint('reviews', __name__, url_prefix='/api/reviews')
    
    # Get reviews for a product
    @reviews_bp.route('/product/<int:product_id>', methods=['GET'])
    def get_product_reviews(product_id):
        try:
            connection = get_db_connection()
            if not connection:
                return jsonify({'error': 'Database connection failed'}), 500
            
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT r.*, c.first_name, c.last_name, c.email
                FROM reviews r
                JOIN customers c ON r.customer_id = c.customer_id
                WHERE r.product_id = %s
                ORDER BY r.review_date DESC
            """, (product_id,))
            
            reviews = cursor.fetchall()
            cursor.close()
            connection.close()
            
            return jsonify({'reviews': reviews})
        
        except Exception as e:
            print(f"Get reviews error: {e}")
            return jsonify({'error': 'Failed to fetch reviews'}), 500
    
    # Create review
    @reviews_bp.route('/', methods=['POST'])
    @token_required
    def create_review(current_user):
        try:
            customer_id = current_user['customer_id']
            data = request.get_json()
            
            required_fields = ['product_id', 'rating', 'review_text']
            for field in required_fields:
                if field not in data:
                    return jsonify({'error': f'Missing required field: {field}'}), 400
            
            product_id = data['product_id']
            rating = data['rating']
            
            if not (1 <= rating <= 5):
                return jsonify({'error': 'Rating must be between 1 and 5'}), 400
            
            connection = get_db_connection()
            if not connection:
                return jsonify({'error': 'Database connection failed'}), 500
            
            cursor = connection.cursor(dictionary=True)
            
            # Check if customer purchased this product
            cursor.execute("""
                SELECT COUNT(*) as count FROM order_items oi
                JOIN orders o ON oi.order_id = o.order_id
                WHERE o.customer_id = %s AND oi.product_id = %s
                AND o.order_status IN ('delivered', 'completed', 'confirmed')
            """, (customer_id, product_id))
            
            purchase = cursor.fetchone()
            if purchase['count'] == 0:
                cursor.close()
                connection.close()
                return jsonify({'error': 'Can only review products you have purchased'}), 403
            
            # Check if review already exists
            cursor.execute("""
                SELECT * FROM reviews WHERE customer_id = %s AND product_id = %s
            """, (customer_id, product_id))
            
            existing = cursor.fetchone()
            if existing:
                # Update existing review
                cursor.execute("""
                    UPDATE reviews 
                    SET rating = %s, review_title = %s, review_text = %s, review_date = NOW()
                    WHERE review_id = %s
                """, (rating, data.get('review_title', ''), data['review_text'], existing['review_id']))
            else:
                # Create new review
                cursor.execute("""
                    INSERT INTO reviews (
                        product_id, customer_id, rating, review_title, review_text, is_verified
                    ) VALUES (%s, %s, %s, %s, %s, TRUE)
                """, (product_id, customer_id, rating, data.get('review_title', ''), data['review_text']))
            
            connection.commit()
            cursor.close()
            connection.close()
            
            return jsonify({'message': 'Review submitted successfully'}), 201
        
        except Exception as e:
            print(f"Create review error: {e}")
            return jsonify({'error': 'Failed to create review'}), 500
    
    # Get user's reviews
    @reviews_bp.route('/user/my-reviews', methods=['GET'])
    @token_required
    def get_user_reviews(current_user):
        try:
            customer_id = current_user['customer_id']
            connection = get_db_connection()
            if not connection:
                return jsonify({'error': 'Database connection failed'}), 500
            
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT r.*, p.product_name, p.image
                FROM reviews r
                JOIN products p ON r.product_id = p.product_id
                WHERE r.customer_id = %s
                ORDER BY r.review_date DESC
            """, (customer_id,))
            
            reviews = cursor.fetchall()
            cursor.close()
            connection.close()
            
            return jsonify({'reviews': reviews})
        
        except Exception as e:
            print(f"Get user reviews error: {e}")
            return jsonify({'error': 'Failed to fetch reviews'}), 500
    
    # Delete review
    @reviews_bp.route('/<int:review_id>', methods=['DELETE'])
    @token_required
    def delete_review(current_user, review_id):
        try:
            customer_id = current_user['customer_id']
            connection = get_db_connection()
            if not connection:
                return jsonify({'error': 'Database connection failed'}), 500
            
            cursor = connection.cursor()
            
            cursor.execute("""
                DELETE FROM reviews 
                WHERE review_id = %s AND customer_id = %s
            """, (review_id, customer_id))
            
            if cursor.rowcount == 0:
                connection.close()
                return jsonify({'error': 'Review not found'}), 404
            
            connection.commit()
            cursor.close()
            connection.close()
            
            return jsonify({'message': 'Review deleted successfully'})
        
        except Exception as e:
            print(f"Delete review error: {e}")
            return jsonify({'error': 'Failed to delete review'}), 500
    
    return reviews_bp
