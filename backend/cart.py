from flask import Blueprint, request, jsonify
from middleware import token_required
from database import db_pool

cart_bp = Blueprint('cart', __name__)

@cart_bp.route('/', methods=['GET'])
@token_required
def get_cart():
    try:
        customer_id = request.user['customer_id']
        conn = db_pool.get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT cart_id FROM shopping_cart WHERE customer_id = %s", (customer_id,))
        cart = cursor.fetchone()

        if not cart:
            return jsonify({"items": [], "total": 0, "item_count": 0})

        cursor.execute("""
            SELECT ci.*, p.product_name, p.price, p.stock_quantity, p.sku
            FROM cart_items ci
            JOIN products p ON ci.product_id = p.product_id
            WHERE ci.cart_id = %s
        """, (cart['cart_id'],))
        items = cursor.fetchall()

        total = sum(item['price'] * item['quantity'] for item in items)
        item_count = sum(item['quantity'] for item in items)

        cursor.close()
        conn.close()

        return jsonify({
            "items": items,
            "total": total,
            "item_count": item_count
        })
    except Exception as e:
        print('Get cart error:', e)
        return jsonify({"error": "Failed to fetch cart"}), 500

@cart_bp.route('/items', methods=['POST'])
@token_required
def add_to_cart():
    try:
        customer_id = request.user['customer_id']
        data = request.get_json()
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)

        conn = db_pool.get_connection()
        cursor = conn.cursor()

        # Get or create cart
        cursor.execute("SELECT cart_id FROM shopping_cart WHERE customer_id = %s", (customer_id,))
        cart = cursor.fetchone()
        if not cart:
            cursor.execute("INSERT INTO shopping_cart (customer_id) VALUES (%s)", (customer_id,))
            cart_id = cursor.lastrowid
        else:
            cart_id = cart[0]

        # Check if item exists in cart
        cursor.execute("SELECT * FROM cart_items WHERE cart_id = %s AND product_id = %s", (cart_id, product_id))
        existing = cursor.fetchone()
        if existing:
            cursor.execute("UPDATE cart_items SET quantity = quantity + %s WHERE cart_item_id = %s", (quantity, existing[0]))
        else:
            cursor.execute("INSERT INTO cart_items (cart_id, product_id, quantity) VALUES (%s, %s, %s)", (cart_id, product_id, quantity))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Item added to cart"})
    except Exception as e:
        print('Add to cart error:', e)
        return jsonify({"error": "Failed to add item to cart"}), 500

# Similarly, implement update and delete endpoints