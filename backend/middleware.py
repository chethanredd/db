import jwt
from flask import request, jsonify
import os

def token_required(f):
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        if not token:
            return jsonify({"error": "Access token required"}), 401
        try:
            data = jwt.decode(token, os.getenv('JWT_SECRET', 'your-secret-key'), algorithms=['HS256'])
            request.user = data
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 403
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 403
        return f(*args, **kwargs)
    decorated.__name__ = f.__name__
    return decorated