# admin_routes.py
from flask import Blueprint, request, jsonify
from mysql.connector import Error
from functools import wraps
import jwt
import mysql.connector
import os
from dotenv import load_dotenv

def create_admin_bp(app):
    """Factory function to create admin blueprint with app reference"""
    
    def get_db_connection():
        load_dotenv()
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
    
    admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')
    
    def admin_required(f):
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
                # Check if user is admin (you'll need to implement this check)
                # For now, we'll assume any authenticated user can access admin routes
                current_user = data
            except:
                return jsonify({'error': 'Token is invalid'}), 401
            
            return f(current_user, *args, **kwargs)
        return decorated

    # Admin - Get all products with details
    @admin_bp.route('/products', methods=['GET'])
    @admin_required
    def get_all_products(current_user):
        try:
            connection = get_db_connection()
            if not connection:
                return jsonify({'error': 'Database connection failed'}), 500
            
            cursor = connection.cursor(dictionary=True)
            
            page = int(request.args.get('page', 1))
            limit = int(request.args.get('limit', 10))
            offset = (page - 1) * limit
            
            cursor.execute("""
                SELECT 
                    p.product_id,
                    p.product_name,
                    p.description,
                    p.price,
                    p.cost_price,
                    p.stock_quantity,
                    p.sku,
                    p.brand,
                    p.weight,
                    p.dimensions,
                    p.color,
                    p.size,
                    p.is_active,
                    p.featured,
                    p.image,
                    p.created_at,
                    p.updated_at,
                    GROUP_CONCAT(DISTINCT c.category_name) as categories,
                    COALESCE(AVG(r.rating), 0) as avg_rating,
                    COUNT(DISTINCT r.review_id) as review_count,
                    COUNT(DISTINCT oi.order_item_id) as total_sold
                FROM products p
                LEFT JOIN product_categories pc ON p.product_id = pc.product_id
                LEFT JOIN categories c ON pc.category_id = c.category_id
                LEFT JOIN reviews r ON p.product_id = r.product_id
                LEFT JOIN order_items oi ON p.product_id = oi.product_id
                GROUP BY p.product_id
                ORDER BY p.created_at DESC
                LIMIT %s OFFSET %s
            """, (limit, offset))
            
            products = cursor.fetchall()
            
            # Get total count for pagination
            cursor.execute("SELECT COUNT(*) as total FROM products")
            total = cursor.fetchone()['total']
            
            cursor.close()
            connection.close()
            
            return jsonify({
                'products': products,
                'total': total,
                'page': page,
                'limit': limit,
                'total_pages': (total + limit - 1) // limit
            })
            
        except Exception as e:
            print(f"Get all products error: {e}")
            return jsonify({'error': 'Failed to fetch products'}), 500

    # Admin - Create new product
    @admin_bp.route('/products', methods=['POST'])
    @admin_required
    def create_product(current_user):
        try:
            data = request.get_json()
            
            required_fields = ['product_name', 'description', 'price', 'sku']
            for field in required_fields:
                if field not in data:
                    return jsonify({'error': f'Missing required field: {field}'}), 400
            
            connection = get_db_connection()
            if not connection:
                return jsonify({'error': 'Database connection failed'}), 500
            
            cursor = connection.cursor(dictionary=True)
            
            # Check if SKU already exists
            cursor.execute("SELECT product_id FROM products WHERE sku = %s", (data['sku'],))
            if cursor.fetchone():
                cursor.close()
                connection.close()
                return jsonify({'error': 'SKU already exists'}), 400
            
            # Insert product
            cursor.execute("""
                INSERT INTO products (
                    product_name, description, price, cost_price, stock_quantity,
                    sku, brand, weight, dimensions, color, size, is_active, featured, image
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                data['product_name'],
                data.get('description', ''),
                data['price'],
                data.get('cost_price'),
                data.get('stock_quantity', 0),
                data['sku'],
                data.get('brand'),
                data.get('weight'),
                data.get('dimensions'),
                data.get('color'),
                data.get('size'),
                data.get('is_active', True),
                data.get('featured', False),
                data.get('image')
            ))
            
            product_id = cursor.lastrowid
            
            # Handle categories
            if 'categories' in data and data['categories']:
                for category_id in data['categories']:
                    cursor.execute(
                        "INSERT INTO product_categories (product_id, category_id) VALUES (%s, %s)",
                        (product_id, category_id)
                    )
            
            connection.commit()
            cursor.close()
            connection.close()
            
            return jsonify({
                'message': 'Product created successfully',
                'product_id': product_id
            }), 201
            
        except Exception as e:
            print(f"Create product error: {e}")
            return jsonify({'error': 'Failed to create product'}), 500

    # Admin - Update product
    @admin_bp.route('/products/<int:product_id>', methods=['PUT'])
    @admin_required
    def update_product(current_user, product_id):
        try:
            data = request.get_json()
            
            connection = get_db_connection()
            if not connection:
                return jsonify({'error': 'Database connection failed'}), 500
            
            cursor = connection.cursor(dictionary=True)
            
            # Check if product exists
            cursor.execute("SELECT product_id FROM products WHERE product_id = %s", (product_id,))
            if not cursor.fetchone():
                cursor.close()
                connection.close()
                return jsonify({'error': 'Product not found'}), 404
            
            # Update product
            update_fields = []
            update_values = []
            
            fields_mapping = {
                'product_name': 'product_name',
                'description': 'description',
                'price': 'price',
                'cost_price': 'cost_price',
                'stock_quantity': 'stock_quantity',
                'brand': 'brand',
                'weight': 'weight',
                'dimensions': 'dimensions',
                'color': 'color',
                'size': 'size',
                'is_active': 'is_active',
                'featured': 'featured',
                'image': 'image'
            }
            
            for field, db_field in fields_mapping.items():
                if field in data:
                    update_fields.append(f"{db_field} = %s")
                    update_values.append(data[field])
            
            if update_fields:
                update_values.append(product_id)
                cursor.execute(
                    f"UPDATE products SET {', '.join(update_fields)} WHERE product_id = %s",
                    update_values
                )
            
            # Update categories if provided
            if 'categories' in data:
                # Remove existing categories
                cursor.execute("DELETE FROM product_categories WHERE product_id = %s", (product_id,))
                
                # Add new categories
                if data['categories']:
                    for category_id in data['categories']:
                        cursor.execute(
                            "INSERT INTO product_categories (product_id, category_id) VALUES (%s, %s)",
                            (product_id, category_id)
                        )
            
            connection.commit()
            cursor.close()
            connection.close()
            
            return jsonify({'message': 'Product updated successfully'})
            
        except Exception as e:
            print(f"Update product error: {e}")
            return jsonify({'error': 'Failed to update product'}), 500

    # Admin - Delete product (soft delete)
    @admin_bp.route('/products/<int:product_id>', methods=['DELETE'])
    @admin_required
    def delete_product(current_user, product_id):
        try:
            connection = get_db_connection()
            if not connection:
                return jsonify({'error': 'Database connection failed'}), 500
            
            cursor = connection.cursor()
            
            # Soft delete by setting is_active to False
            cursor.execute("UPDATE products SET is_active = FALSE WHERE product_id = %s", (product_id,))
            
            connection.commit()
            cursor.close()
            connection.close()
            
            return jsonify({'message': 'Product deleted successfully'})
            
        except Exception as e:
            print(f"Delete product error: {e}")
            return jsonify({'error': 'Failed to delete product'}), 500

    # Admin - Get all categories
    @admin_bp.route('/categories', methods=['GET'])
    @admin_required
    def get_categories(current_user):
        try:
            connection = get_db_connection()
            if not connection:
                return jsonify({'error': 'Database connection failed'}), 500
            
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT c.*, 
                       COUNT(pc.product_id) as product_count,
                       parent.category_name as parent_name
                FROM categories c
                LEFT JOIN product_categories pc ON c.category_id = pc.category_id
                LEFT JOIN categories parent ON c.parent_category_id = parent.category_id
                GROUP BY c.category_id
                ORDER BY c.category_name
            """)
            
            categories = cursor.fetchall()
            
            cursor.close()
            connection.close()
            
            return jsonify(categories)
            
        except Exception as e:
            print(f"Get categories error: {e}")
            return jsonify({'error': 'Failed to fetch categories'}), 500

    # Admin - Get dashboard statistics
    @admin_bp.route('/dashboard', methods=['GET'])
    @admin_required
    def get_dashboard_stats(current_user):
        try:
            connection = get_db_connection()
            if not connection:
                return jsonify({'error': 'Database connection failed'}), 500
            
            cursor = connection.cursor(dictionary=True)
            
            # Total sales
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_orders,
                    SUM(total_amount) as total_revenue,
                    AVG(total_amount) as avg_order_value
                FROM orders 
                WHERE order_status IN ('delivered', 'completed')
            """)
            sales_stats = cursor.fetchone()
            
            # Product statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_products,
                    SUM(stock_quantity) as total_stock,
                    SUM(CASE WHEN stock_quantity = 0 THEN 1 ELSE 0 END) as out_of_stock
                FROM products 
                WHERE is_active = TRUE
            """)
            product_stats = cursor.fetchone()
            
            # Customer statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_customers,
                    COUNT(CASE WHEN last_login >= DATE_SUB(NOW(), INTERVAL 30 DAY) THEN 1 END) as active_customers
                FROM customers 
                WHERE is_active = TRUE
            """)
            customer_stats = cursor.fetchone()
            
            # Recent orders
            cursor.execute("""
                SELECT o.order_id, o.order_date, o.total_amount, o.order_status,
                       CONCAT(c.first_name, ' ', c.last_name) as customer_name
                FROM orders o
                JOIN customers c ON o.customer_id = c.customer_id
                ORDER BY o.order_date DESC
                LIMIT 10
            """)
            recent_orders = cursor.fetchall()
            
            cursor.close()
            connection.close()
            
            return jsonify({
                'sales': sales_stats,
                'products': product_stats,
                'customers': customer_stats,
                'recent_orders': recent_orders
            })
            
        except Exception as e:
            print(f"Get dashboard stats error: {e}")
            return jsonify({'error': 'Failed to fetch dashboard statistics'}), 500

    # Test database functions and procedures
    @admin_bp.route('/test-db-functions', methods=['GET'])
    @admin_required
    def test_db_functions(current_user):
        try:
            connection = get_db_connection()
            if not connection:
                return jsonify({'error': 'Database connection failed'}), 500
            
            cursor = connection.cursor(dictionary=True)
            
            results = {}
            
            # Test get_customer_total_spent function
            cursor.execute("SELECT get_customer_total_spent(1) as total_spent")
            results['customer_total_spent'] = cursor.fetchone()
            
            # Test calculate_order_tax function
            cursor.execute("SELECT calculate_order_tax(1) as order_tax")
            results['order_tax'] = cursor.fetchone()
            
            # Test generate_sales_report procedure (call it and fetch results)
            cursor.callproc('generate_sales_report', ['2024-01-01', '2024-12-31'])
            for result in cursor.stored_results():
                sales_report = result.fetchone()
                results['sales_report'] = sales_report
            
            cursor.close()
            connection.close()
            
            return jsonify({
                'message': 'Database functions tested successfully',
                'results': results
            })
            
        except Exception as e:
            print(f"Test DB functions error: {e}")
            return jsonify({'error': f'Failed to test database functions: {str(e)}'}), 500
    
    return admin_bp
