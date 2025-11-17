# addresses.py
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

def create_addresses_bp(app):
    from flask import Blueprint
    addresses_bp = Blueprint('addresses', __name__, url_prefix='/api/addresses')
    
    # Get all addresses for authenticated user
    @addresses_bp.route('/', methods=['GET'])
    @token_required
    def get_addresses(current_user):
        try:
            customer_id = current_user['customer_id']
            print(f"📦 Fetching addresses for customer {customer_id}")
            
            connection = get_db_connection()
            if not connection:
                return jsonify({'error': 'Database connection failed'}), 500
            
            cursor = connection.cursor(dictionary=True)
            
            # Get all addresses linked to this customer - include both shipping and billing address IDs
            cursor.execute("""
                SELECT a.* FROM addresses a
                WHERE a.customer_id = %s
                ORDER BY a.created_at DESC
            """, (customer_id,))
            
            addresses = cursor.fetchall()
            print(f"Found {len(addresses)} addresses for customer {customer_id}")
            for addr in addresses:
                print(f"  - Address {addr['address_id']}: {addr['street_address']}, {addr['city']}")
            cursor.close()
            connection.close()
            
            return jsonify({'addresses': addresses})
        
        except Exception as e:
            print(f"Get addresses error: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': 'Failed to fetch addresses'}), 500
    
    # Create new address
    @addresses_bp.route('/', methods=['POST'])
    @token_required
    def create_address(current_user):
        try:
            data = request.get_json()
            print(f"📦 Creating address for customer {current_user['customer_id']}")
            print(f"📋 Address data: {data}")
            
            required_fields = ['street_address', 'city', 'state', 'postal_code']
            
            for field in required_fields:
                if field not in data:
                    error_msg = f'Missing required field: {field}'
                    print(f"❌ {error_msg}")
                    return jsonify({'error': error_msg}), 400
            
            connection = get_db_connection()
            if not connection:
                print("❌ Database connection failed")
                return jsonify({'error': 'Database connection failed'}), 500
            
            cursor = connection.cursor(dictionary=True)
            customer_id = current_user['customer_id']
            
            country = data.get('country', 'India')
            address_type = data.get('address_type', 'both')
            
            print(f"💾 Inserting address: {data['street_address']}, {data['city']}, {data['state']}")
            cursor.execute("""
                INSERT INTO addresses (
                    street_address, city, state, postal_code, country, address_type, customer_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                data['street_address'], data['city'], data['state'],
                data['postal_code'], country, address_type, customer_id
            ))
            
            address_id = cursor.lastrowid
            connection.commit()
            print(f"✅ Address inserted with ID: {address_id}")
            
            # Update customer shipping address
            if data.get('set_as_shipping'):
                print(f"📍 Setting as shipping address for customer {customer_id}")
                cursor.execute("""
                    UPDATE customers SET shipping_address_id = %s WHERE customer_id = %s
                """, (address_id, customer_id))
                connection.commit()
                print(f"✅ Updated shipping address {address_id}")
            
            # Update customer billing address
            if data.get('set_as_billing'):
                print(f"💳 Setting as billing address for customer {customer_id}")
                cursor.execute("""
                    UPDATE customers SET billing_address_id = %s WHERE customer_id = %s
                """, (address_id, customer_id))
                connection.commit()
                print(f"✅ Updated billing address {address_id}")
            
            # If it's the first address, set as both shipping and billing by default
            print(f"🔍 Checking if this is first address for customer {customer_id}")
            cursor.execute("""
                SELECT shipping_address_id, billing_address_id FROM customers WHERE customer_id = %s
            """, (customer_id,))
            customer = cursor.fetchone()
            
            if customer and not customer['shipping_address_id']:
                print(f"📍 Setting first address as default shipping")
                cursor.execute("""
                    UPDATE customers SET shipping_address_id = %s WHERE customer_id = %s
                """, (address_id, customer_id))
                connection.commit()
                print(f"✅ Updated default shipping address {address_id}")
            
            if customer and not customer['billing_address_id']:
                print(f"💳 Setting first address as default billing")
                cursor.execute("""
                    UPDATE customers SET billing_address_id = %s WHERE customer_id = %s
                """, (address_id, customer_id))
                connection.commit()
                print(f"✅ Updated default billing address {address_id}")
            
            cursor.close()
            connection.close()
            
            print(f"✅ Address creation complete. ID: {address_id}")
            return jsonify({
                'address_id': address_id,
                'message': 'Address created and updated successfully'
            }), 201
        
        except Exception as e:
            print(f"❌ Create address error: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500
    
    # Update address
    @addresses_bp.route('/<int:address_id>', methods=['PUT'])
    @token_required
    def update_address(current_user, address_id):
        try:
            data = request.get_json()
            connection = get_db_connection()
            if not connection:
                return jsonify({'error': 'Database connection failed'}), 500
            
            cursor = connection.cursor()
            
            update_fields = []
            update_values = []
            
            if 'street_address' in data:
                update_fields.append('street_address = %s')
                update_values.append(data['street_address'])
            if 'city' in data:
                update_fields.append('city = %s')
                update_values.append(data['city'])
            if 'state' in data:
                update_fields.append('state = %s')
                update_values.append(data['state'])
            if 'postal_code' in data:
                update_fields.append('postal_code = %s')
                update_values.append(data['postal_code'])
            if 'country' in data:
                update_fields.append('country = %s')
                update_values.append(data['country'])
            if 'address_type' in data:
                update_fields.append('address_type = %s')
                update_values.append(data['address_type'])
            
            if not update_fields:
                cursor.close()
                connection.close()
                return jsonify({'error': 'No fields to update'}), 400
            
            update_values.append(address_id)
            update_query = f"UPDATE addresses SET {', '.join(update_fields)} WHERE address_id = %s"
            
            cursor.execute(update_query, update_values)
            connection.commit()
            cursor.close()
            connection.close()
            
            return jsonify({'message': 'Address updated successfully'})
        
        except Exception as e:
            print(f"Update address error: {e}")
            return jsonify({'error': 'Failed to update address'}), 500
    
    # Delete address
    @addresses_bp.route('/<int:address_id>', methods=['DELETE'])
    @token_required
    def delete_address(current_user, address_id):
        try:
            connection = get_db_connection()
            if not connection:
                return jsonify({'error': 'Database connection failed'}), 500
            
            cursor = connection.cursor()
            
            # Check if address is used in any orders
            cursor.execute("""
                SELECT COUNT(*) as count FROM orders 
                WHERE shipping_address_id = %s OR billing_address_id = %s
            """, (address_id, address_id))
            
            result = cursor.fetchone()
            if result[0] > 0:
                cursor.close()
                connection.close()
                return jsonify({'error': 'Cannot delete address used in orders'}), 400
            
            cursor.execute("DELETE FROM addresses WHERE address_id = %s", (address_id,))
            connection.commit()
            cursor.close()
            connection.close()
            
            return jsonify({'message': 'Address deleted successfully'})
        
        except Exception as e:
            print(f"Delete address error: {e}")
            return jsonify({'error': 'Failed to delete address'}), 500
    
    return addresses_bp
