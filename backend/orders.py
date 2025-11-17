# orders.py
from flask import request, jsonify
from functools import wraps
import jwt
import os
from mysql.connector import Error
import mysql.connector

# Try to import email service, but don't fail if it's not available
try:
    from email_service import email_service
except ImportError:
    email_service = None

def token_required_except_options(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Skip token validation for CORS preflight requests
        if request.method == 'OPTIONS':
            return f(None, *args, **kwargs)
        
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

def create_orders_bp(app):
    from flask import Blueprint
    orders_bp = Blueprint('orders', __name__, url_prefix='/api/orders')
    
    # Get all orders for authenticated user
    @orders_bp.route('/', methods=['GET', 'OPTIONS'], strict_slashes=False)
    @token_required_except_options
    def get_orders(current_user):
        # Skip processing for CORS preflight
        if request.method == 'OPTIONS':
            return '', 200
        
        try:
            customer_id = current_user['customer_id']
            connection = get_db_connection()
            if not connection:
                return jsonify({'error': 'Database connection failed'}), 500
            
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT o.*, c.first_name, c.last_name, c.email
                FROM orders o
                JOIN customers c ON o.customer_id = c.customer_id
                WHERE o.customer_id = %s
                ORDER BY o.order_date DESC
            """, (customer_id,))
            
            orders = cursor.fetchall()
            
            # Convert Decimal to float for JSON
            for order in orders:
                if 'total_amount' in order:
                    order['total_amount'] = float(order['total_amount'])
                if 'shipping_amount' in order:
                    order['shipping_amount'] = float(order['shipping_amount'])
                if 'tax_amount' in order:
                    order['tax_amount'] = float(order['tax_amount'])
                if 'discount_amount' in order:
                    order['discount_amount'] = float(order['discount_amount'])
            
            cursor.close()
            connection.close()
            
            return jsonify({'orders': orders})
        
        except Exception as e:
            print(f"Get orders error: {e}")
            return jsonify({'error': 'Failed to fetch orders'}), 500
    
    # Get single order with items
    @orders_bp.route('/<int:order_id>', methods=['GET', 'OPTIONS'], strict_slashes=False)
    @token_required_except_options
    def get_order(current_user, order_id):
        # Skip processing for CORS preflight
        if request.method == 'OPTIONS':
            return '', 200
        
        try:
            customer_id = current_user['customer_id']
            connection = get_db_connection()
            if not connection:
                return jsonify({'error': 'Database connection failed'}), 500
            
            cursor = connection.cursor(dictionary=True)
            
            # Get order
            cursor.execute("""
                SELECT o.*, c.first_name, c.last_name, c.email,
                       sa.street_address as ship_street, sa.city as ship_city, sa.state as ship_state,
                       ba.street_address as bill_street, ba.city as bill_city, ba.state as bill_state
                FROM orders o
                JOIN customers c ON o.customer_id = c.customer_id
                LEFT JOIN addresses sa ON o.shipping_address_id = sa.address_id
                LEFT JOIN addresses ba ON o.billing_address_id = ba.address_id
                WHERE o.order_id = %s AND o.customer_id = %s
            """, (order_id, customer_id))
            
            order = cursor.fetchone()
            if not order:
                cursor.close()
                connection.close()
                return jsonify({'error': 'Order not found'}), 404
            
            # Get order items
            cursor.execute("""
                SELECT oi.*, p.product_name, p.image, p.sku
                FROM order_items oi
                JOIN products p ON oi.product_id = p.product_id
                WHERE oi.order_id = %s
            """, (order_id,))
            
            items = cursor.fetchall()
            
            # Get payment info
            cursor.execute("""
                SELECT * FROM payments WHERE order_id = %s
            """, (order_id,))
            
            payment = cursor.fetchone()
            
            # Convert Decimal to float
            order['total_amount'] = float(order['total_amount'])
            order['shipping_amount'] = float(order['shipping_amount'])
            order['tax_amount'] = float(order['tax_amount'])
            order['discount_amount'] = float(order['discount_amount'])
            
            for item in items:
                item['unit_price'] = float(item['unit_price'])
                item['total_price'] = float(item['total_price'])
            
            if payment:
                payment['payment_amount'] = float(payment['payment_amount'])
                payment['refund_amount'] = float(payment['refund_amount'])
            
            cursor.close()
            connection.close()
            
            return jsonify({
                'order': order,
                'items': items,
                'payment': payment
            })
        
        except Exception as e:
            print(f"Get order error: {e}")
            return jsonify({'error': 'Failed to fetch order'}), 500
    
    # Create order from cart
    @orders_bp.route('/create', methods=['POST', 'OPTIONS'], strict_slashes=False)
    @token_required_except_options
    def create_order(current_user):
        # Skip processing for CORS preflight
        if request.method == 'OPTIONS':
            return '', 200
        
        try:
            customer_id = current_user['customer_id']
            data = request.get_json()
            
            shipping_address_id = data.get('shipping_address_id')
            billing_address_id = data.get('billing_address_id')
            payment_method = data.get('payment_method', 'cod')
            
            print(f"📦 Creating order for customer {customer_id}")
            print(f"📍 Shipping address: {shipping_address_id}")
            print(f"💳 Payment method: {payment_method}")
            
            if not shipping_address_id:
                print(f"❌ Missing shipping address")
                return jsonify({'error': 'Shipping address is required'}), 400
            
            connection = get_db_connection()
            if not connection:
                print(f"❌ Database connection failed")
                return jsonify({'error': 'Database connection failed'}), 500
            
            cursor = connection.cursor(dictionary=True)
            
            # Verify shipping address belongs to customer
            print(f"🔍 Verifying shipping address {shipping_address_id}")
            cursor.execute("""
                SELECT address_id FROM addresses 
                WHERE address_id = %s AND customer_id = %s
            """, (shipping_address_id, customer_id))
            
            if not cursor.fetchone():
                cursor.close()
                connection.close()
                print(f"❌ Shipping address not found")
                return jsonify({'error': 'Shipping address not found'}), 404
            
            # Verify billing address if provided
            if billing_address_id:
                print(f"🔍 Verifying billing address {billing_address_id}")
                cursor.execute("""
                    SELECT address_id FROM addresses 
                    WHERE address_id = %s AND customer_id = %s
                """, (billing_address_id, customer_id))
                
                if not cursor.fetchone():
                    cursor.close()
                    connection.close()
                    print(f"❌ Billing address not found")
                    return jsonify({'error': 'Billing address not found'}), 404
            
            # Get cart
            print(f"📦 Fetching cart for customer {customer_id}")
            cursor.execute("SELECT cart_id FROM shopping_cart WHERE customer_id = %s", (customer_id,))
            cart = cursor.fetchone()
            
            if not cart:
                cursor.close()
                connection.close()
                print(f"❌ Cart not found")
                return jsonify({'error': 'Cart not found'}), 404
            
            # Get cart items
            print(f"📦 Fetching cart items")
            cursor.execute("""
                SELECT ci.*, p.price
                FROM cart_items ci
                JOIN products p ON ci.product_id = p.product_id
                WHERE ci.cart_id = %s
            """, (cart['cart_id'],))
            
            cart_items = cursor.fetchall()
            
            if not cart_items:
                cursor.close()
                connection.close()
                print(f"❌ Cart is empty")
                return jsonify({'error': 'Cart is empty'}), 400
            
            print(f"✅ Found {len(cart_items)} items in cart")
            
            # Calculate totals - convert Decimal to float
            subtotal = sum(float(item['price']) * item['quantity'] for item in cart_items)
            shipping_amount = 0 if subtotal >= 1000 else 100  # Free shipping above 1000
            tax_amount = subtotal * 0.18  # 18% GST
            discount_amount = 0
            total_amount = subtotal + shipping_amount + tax_amount - discount_amount
            
            print(f"💰 Subtotal: {subtotal}, Tax: {tax_amount}, Shipping: {shipping_amount}")
            print(f"💰 Total: {total_amount}")
            
            # Create order
            print(f"➕ Creating order in database")
            cursor.execute("""
                INSERT INTO orders (
                    customer_id, order_status, total_amount, 
                    shipping_amount, tax_amount, discount_amount,
                    shipping_address_id, billing_address_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                customer_id, 'pending', total_amount,
                shipping_amount, tax_amount, discount_amount,
                shipping_address_id, billing_address_id or shipping_address_id
            ))
            
            order_id = cursor.lastrowid
            print(f"✅ Order created with ID: {order_id}")
            
            # Add order items (THIS TRIGGERS THE STOCK UPDATE TRIGGER)
            print(f"➕ Adding items to order")
            for item in cart_items:
                item_price = float(item['price'])
                item_total = item_price * item['quantity']
                cursor.execute("""
                    INSERT INTO order_items (
                        order_id, product_id, quantity, unit_price, total_price
                    ) VALUES (%s, %s, %s, %s, %s)
                """, (
                    order_id, item['product_id'], item['quantity'],
                    item_price, item_total
                ))
                print(f"   ✅ Added product {item['product_id']}: {item['quantity']} units")
            
            # Create payment record
            print(f"💳 Creating payment record with method: {payment_method}")
            cursor.execute("""
                INSERT INTO payments (
                    order_id, payment_method, payment_status, payment_amount
                ) VALUES (%s, %s, %s, %s)
            """, (order_id, payment_method, 'pending', total_amount))
            
            payment_id = cursor.lastrowid
            print(f"✅ Payment record created with ID: {payment_id}")
            
            # Clear cart
            print(f"🧹 Clearing cart")
            cursor.execute("DELETE FROM cart_items WHERE cart_id = %s", (cart['cart_id'],))
            
            connection.commit()
            print(f"✅ Order creation complete. All changes committed to database.")
            
            # Fetch customer details for email
            cursor.execute("""
                SELECT email, first_name, last_name FROM customers WHERE customer_id = %s
            """, (customer_id,))
            customer = cursor.fetchone()
            
            # Fetch order items with product names for email
            cursor.execute("""
                SELECT oi.quantity, oi.unit_price, oi.total_price, p.product_name
                FROM order_items oi
                JOIN products p ON oi.product_id = p.product_id
                WHERE oi.order_id = %s
            """, (order_id,))
            email_items = cursor.fetchall()
            
            cursor.close()
            connection.close()
            
            # Note: Email service commented out to avoid dependency issues
            # Uncomment when email_service is properly configured
            # if customer:
            #     email_items_list = [
            #         {
            #             'product_name': item[3],
            #             'quantity': item[0],
            #             'unit_price': float(item[1]),
            #             'total_price': float(item[2])
            #         }
            #         for item in email_items
            #     ]
            #     email_service.send_order_confirmation(...)
            
            print(f"✅ Order {order_id} ready for payment processing")
            
            return jsonify({
                'order_id': order_id,
                'total_amount': float(total_amount),
                'subtotal': float(subtotal),
                'tax_amount': float(tax_amount),
                'shipping_amount': float(shipping_amount),
                'payment_method': payment_method,
                'message': 'Order created successfully. Ready for payment processing.'
            }), 201
        
        except Exception as e:
            print(f"❌ Create order error: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500
    
    # Update order status (admin only)
    @orders_bp.route('/<int:order_id>/status', methods=['PUT', 'OPTIONS'], strict_slashes=False)
    @token_required_except_options
    def update_order_status(current_user, order_id):
        # Skip processing for CORS preflight
        if request.method == 'OPTIONS':
            return '', 200
        
        try:
            # Check if admin
            if not current_user.get('is_admin'):
                return jsonify({'error': 'Admin access required'}), 403
            
            data = request.get_json()
            new_status = data.get('status')
            
            valid_statuses = ['pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled', 'returned']
            if new_status not in valid_statuses:
                return jsonify({'error': 'Invalid status'}), 400
            
            connection = get_db_connection()
            if not connection:
                return jsonify({'error': 'Database connection failed'}), 500
            
            cursor = connection.cursor()
            
            cursor.execute("""
                UPDATE orders SET order_status = %s WHERE order_id = %s
            """, (new_status, order_id))
            
            connection.commit()
            cursor.close()
            connection.close()
            
            return jsonify({'message': 'Order status updated successfully'})
        
        except Exception as e:
            print(f"Update order status error: {e}")
            return jsonify({'error': 'Failed to update order status'}), 500
    
    return orders_bp
