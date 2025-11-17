# payments.py - Payment Processing Module
from flask import request, jsonify, Blueprint
from functools import wraps
import jwt
import os
from mysql.connector import Error
import mysql.connector
import uuid
from datetime import datetime

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

def create_payments_bp(app):
    payments_bp = Blueprint('payments', __name__, url_prefix='/api/payments')
    
    # Process payment
    @payments_bp.route('/process', methods=['POST'])
    @token_required
    def process_payment(current_user):
        """
        Process payment for an order
        Supports multiple payment methods:
        - credit_card
        - debit_card
        - upi
        - net_banking
        - wallet
        - cod (cash on delivery)
        """
        try:
            customer_id = current_user['customer_id']
            data = request.get_json()
            
            order_id = data.get('order_id')
            payment_method = data.get('payment_method')
            
            print(f"💳 Processing payment for order {order_id}")
            print(f"💰 Payment method: {payment_method}")
            
            if not order_id or not payment_method:
                return jsonify({'error': 'Missing order_id or payment_method'}), 400
            
            valid_methods = ['credit_card', 'debit_card', 'upi', 'net_banking', 'wallet', 'cod']
            if payment_method not in valid_methods:
                return jsonify({'error': f'Invalid payment method. Valid methods: {valid_methods}'}), 400
            
            connection = get_db_connection()
            if not connection:
                return jsonify({'error': 'Database connection failed'}), 500
            
            cursor = connection.cursor(dictionary=True)
            
            # Verify order belongs to customer
            print(f"🔍 Verifying order {order_id} belongs to customer {customer_id}")
            cursor.execute("""
                SELECT o.order_id, o.total_amount, o.order_status, p.payment_id, p.payment_status
                FROM orders o
                LEFT JOIN payments p ON o.order_id = p.order_id
                WHERE o.order_id = %s AND o.customer_id = %s
            """, (order_id, customer_id))
            
            order = cursor.fetchone()
            
            if not order:
                cursor.close()
                connection.close()
                print(f"❌ Order {order_id} not found for customer {customer_id}")
                return jsonify({'error': 'Order not found'}), 404
            
            print(f"✅ Order verified: Status={order['order_status']}, Amount={order['total_amount']}")
            
            # Check if payment already processed
            if order['payment_id'] and order['payment_status'] in ['completed', 'processing']:
                cursor.close()
                connection.close()
                print(f"⚠️ Payment already {order['payment_status']} for order {order_id}")
                return jsonify({'error': f'Payment already {order["payment_status"]}'}), 400
            
            # Generate transaction ID
            transaction_id = f"{payment_method.upper()}-{order_id}-{uuid.uuid4().hex[:12].upper()}"
            print(f"🔐 Generated transaction ID: {transaction_id}")
            
            # Simulate payment processing based on method
            payment_status = 'pending'
            payment_gateway = None
            
            if payment_method == 'cod':
                # Cash on delivery - mark as completed but pending
                payment_status = 'completed'
                payment_gateway = 'COD'
                print(f"📦 Cash on Delivery selected - Status: {payment_status}")
            
            elif payment_method == 'upi':
                # UPI payment simulation
                payment_status = 'processing'
                payment_gateway = 'Razorpay'
                print(f"📱 UPI Payment processing via {payment_gateway}")
            
            elif payment_method in ['credit_card', 'debit_card']:
                # Card payment simulation
                payment_status = 'processing'
                payment_gateway = 'Stripe'
                print(f"💳 Card Payment processing via {payment_gateway}")
            
            elif payment_method == 'net_banking':
                # Net banking simulation
                payment_status = 'processing'
                payment_gateway = 'ICICI Bank'
                print(f"🏦 Net Banking processing via {payment_gateway}")
            
            elif payment_method == 'wallet':
                # Wallet payment simulation
                payment_status = 'processing'
                payment_gateway = 'Paytm'
                print(f"👛 Wallet Payment processing via {payment_gateway}")
            
            # Update or insert payment record
            if order['payment_id']:
                print(f"♻️ Updating existing payment record {order['payment_id']}")
                cursor.execute("""
                    UPDATE payments 
                    SET payment_method = %s, 
                        payment_status = %s, 
                        transaction_id = %s,
                        payment_gateway = %s,
                        payment_date = NOW()
                    WHERE payment_id = %s
                """, (payment_method, payment_status, transaction_id, payment_gateway, order['payment_id']))
            else:
                print(f"➕ Creating new payment record")
                cursor.execute("""
                    INSERT INTO payments (
                        order_id, payment_method, payment_status, 
                        payment_amount, transaction_id, payment_gateway, payment_date
                    ) VALUES (%s, %s, %s, %s, %s, %s, NOW())
                """, (order_id, payment_method, payment_status, order['total_amount'], transaction_id, payment_gateway))
                
                payment_id = cursor.lastrowid
                print(f"✅ Payment record created with ID: {payment_id}")
            
            connection.commit()
            
            # If payment completed (COD), update order status to confirmed
            if payment_status == 'completed':
                print(f"📋 Updating order status to confirmed")
                cursor.execute("""
                    UPDATE orders SET order_status = 'confirmed' WHERE order_id = %s
                """, (order_id,))
                connection.commit()
                print(f"✅ Order status updated to confirmed")
            
            cursor.close()
            connection.close()
            
            print(f"✅ Payment processing complete. Status: {payment_status}")
            
            return jsonify({
                'message': 'Payment processed successfully',
                'order_id': order_id,
                'transaction_id': transaction_id,
                'payment_method': payment_method,
                'payment_status': payment_status,
                'payment_gateway': payment_gateway,
                'amount': float(order['total_amount'])
            }), 200
        
        except Exception as e:
            print(f"❌ Payment processing error: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': 'Payment processing failed'}), 500
    
    # Get payment details
    @payments_bp.route('/order/<int:order_id>', methods=['GET'])
    @token_required
    def get_payment(current_user, order_id):
        """Get payment details for an order"""
        try:
            customer_id = current_user['customer_id']
            print(f"🔍 Fetching payment for order {order_id}, customer {customer_id}")
            
            connection = get_db_connection()
            if not connection:
                return jsonify({'error': 'Database connection failed'}), 500
            
            cursor = connection.cursor(dictionary=True)
            
            # Verify order belongs to customer
            cursor.execute("""
                SELECT o.order_id FROM orders o
                WHERE o.order_id = %s AND o.customer_id = %s
            """, (order_id, customer_id))
            
            if not cursor.fetchone():
                cursor.close()
                connection.close()
                print(f"❌ Order {order_id} not found")
                return jsonify({'error': 'Order not found'}), 404
            
            # Get payment
            cursor.execute("""
                SELECT * FROM payments WHERE order_id = %s
            """, (order_id,))
            
            payment = cursor.fetchone()
            
            if not payment:
                cursor.close()
                connection.close()
                print(f"⚠️ No payment found for order {order_id}")
                return jsonify({'error': 'Payment not found'}), 404
            
            # Convert Decimal to float
            payment['payment_amount'] = float(payment['payment_amount'])
            payment['refund_amount'] = float(payment['refund_amount'])
            
            cursor.close()
            connection.close()
            
            print(f"✅ Payment retrieved: Status={payment['payment_status']}")
            
            return jsonify({'payment': payment}), 200
        
        except Exception as e:
            print(f"❌ Get payment error: {e}")
            return jsonify({'error': 'Failed to fetch payment'}), 500
    
    # Refund payment
    @payments_bp.route('/<int:payment_id>/refund', methods=['POST'])
    @token_required
    def refund_payment(current_user, payment_id):
        """Process refund for a payment"""
        try:
            customer_id = current_user['customer_id']
            data = request.get_json()
            refund_amount = data.get('refund_amount')
            refund_reason = data.get('reason', 'Customer requested refund')
            
            print(f"💸 Processing refund for payment {payment_id}")
            print(f"💰 Refund amount: {refund_amount}")
            print(f"📝 Reason: {refund_reason}")
            
            connection = get_db_connection()
            if not connection:
                return jsonify({'error': 'Database connection failed'}), 500
            
            cursor = connection.cursor(dictionary=True)
            
            # Get payment and verify it belongs to customer's order
            cursor.execute("""
                SELECT p.*, o.customer_id, o.total_amount
                FROM payments p
                JOIN orders o ON p.order_id = o.order_id
                WHERE p.payment_id = %s AND o.customer_id = %s
            """, (payment_id, customer_id))
            
            payment = cursor.fetchone()
            
            if not payment:
                cursor.close()
                connection.close()
                print(f"❌ Payment not found")
                return jsonify({'error': 'Payment not found'}), 404
            
            print(f"✅ Payment found. Current status: {payment['payment_status']}")
            
            # Check if refund is applicable
            if payment['payment_status'] not in ['completed', 'processing']:
                cursor.close()
                connection.close()
                print(f"⚠️ Cannot refund payment with status: {payment['payment_status']}")
                return jsonify({'error': f'Cannot refund payment with status: {payment["payment_status"]}'}), 400
            
            # Validate refund amount
            if refund_amount > float(payment['payment_amount']):
                cursor.close()
                connection.close()
                print(f"❌ Refund amount exceeds payment amount")
                return jsonify({'error': 'Refund amount exceeds payment amount'}), 400
            
            # Process refund
            print(f"🔄 Processing refund...")
            cursor.execute("""
                UPDATE payments 
                SET payment_status = 'refunded',
                    refund_amount = %s,
                    refund_date = NOW()
                WHERE payment_id = %s
            """, (refund_amount, payment_id))
            
            connection.commit()
            print(f"✅ Refund processed")
            
            # Update order status to cancelled if full refund
            if refund_amount == float(payment['payment_amount']):
                print(f"📋 Full refund - updating order status to cancelled")
                cursor.execute("""
                    UPDATE orders SET order_status = 'cancelled' WHERE order_id = %s
                """, (payment['order_id'],))
                connection.commit()
                print(f"✅ Order cancelled")
            
            cursor.close()
            connection.close()
            
            print(f"✅ Refund complete")
            
            return jsonify({
                'message': 'Refund processed successfully',
                'payment_id': payment_id,
                'refund_amount': float(refund_amount),
                'reason': refund_reason
            }), 200
        
        except Exception as e:
            print(f"❌ Refund error: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': 'Refund processing failed'}), 500
    
    return payments_bp
