from flask import Blueprint, request, jsonify
from database import db_pool

products_bp = Blueprint('products', __name__)

@products_bp.route('/', methods=['GET'])
def get_products():
    try:
        category = request.args.get('category')
        search = request.args.get('search')
        featured = request.args.get('featured')
        limit = request.args.get('limit', 50)
        offset = request.args.get('offset', 0)

        conn = db_pool.get_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT p.*, 
                GROUP_CONCAT(DISTINCT c.category_name) as categories,
                COALESCE(AVG(r.rating), 0) as avg_rating,
                COUNT(DISTINCT r.review_id) as review_count
            FROM products p
            LEFT JOIN product_categories pc ON p.product_id = pc.product_id
            LEFT JOIN categories c ON pc.category_id = c.category_id
            LEFT JOIN reviews r ON p.product_id = r.product_id
            WHERE p.is_active = TRUE
        """
        params = []

        if category:
            query += " AND c.category_name = %s"
            params.append(category)

        if search:
            query += " AND (p.product_name LIKE %s OR p.description LIKE %s)"
            params.append(f"%{search}%")
            params.append(f"%{search}%")

        if featured == 'true':
            query += " AND p.featured = TRUE"

        query += " GROUP BY p.product_id ORDER BY p.created_at DESC LIMIT %s OFFSET %s"
        params.append(int(limit))
        params.append(int(offset))

        cursor.execute(query, params)
        products = cursor.fetchall()

        # Format the products
        for product in products:
            product['avg_rating'] = float(product['avg_rating']) if product['avg_rating'] else 0.0
            product['review_count'] = product['review_count']

        cursor.close()
        conn.close()

        return jsonify({
            "products": products,
            "count": len(products)
        })
    except Exception as e:
        print('Get products error:', e)
        return jsonify({"error": "Failed to fetch products"}), 500

@products_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    try:
        conn = db_pool.get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT p.*, 
                GROUP_CONCAT(DISTINCT c.category_name) as categories,
                COALESCE(AVG(r.rating), 0) as avg_rating,
                COUNT(DISTINCT r.review_id) as review_count
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
            conn.close()
            return jsonify({"error": "Product not found"}), 404

        product['avg_rating'] = float(product['avg_rating']) if product['avg_rating'] else 0.0
        product['review_count'] = product['review_count']

        cursor.close()
        conn.close()

        return jsonify(product)
    except Exception as e:
        print('Get product error:', e)
        return jsonify({"error": "Failed to fetch product"}), 500