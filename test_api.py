#!/usr/bin/env python3
"""
ShopScale Backend Test & Verification Script
Tests all API endpoints and verifies database connection
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000/api"

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_section(title):
    print(f"\n{BLUE}{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}{RESET}\n")

def print_success(message):
    print(f"{GREEN}✓ {message}{RESET}")

def print_error(message):
    print(f"{RED}✗ {message}{RESET}")

def print_info(message):
    print(f"{YELLOW}ℹ {message}{RESET}")

def test_health():
    """Test API health endpoint"""
    print_section("Testing API Health")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print_success(f"API is running - Status: {data['status']}")
            print_success(f"Database: {data['database']}")
            return True
        else:
            print_error(f"Health check failed - Status: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Cannot connect to API: {e}")
        return False

def test_products():
    """Test product endpoints"""
    print_section("Testing Product Endpoints")
    try:
        response = requests.get(f"{BASE_URL}/products")
        if response.status_code == 200:
            data = response.json()
            count = data['count']
            print_success(f"Fetched {count} products")
            if count > 0:
                product = data['products'][0]
                print_info(f"Sample product: {product.get('product_name')} - ₹{product.get('price')}")
            return True
        else:
            print_error(f"Failed to fetch products - Status: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Product test failed: {e}")
        return False

def test_auth():
    """Test authentication endpoints"""
    print_section("Testing Authentication")
    
    # Test login with test credentials
    try:
        login_data = {
            "email": "rajesh.kumar@email.com",
            "password": "password123"
        }
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            customer = data.get('customer')
            print_success(f"Login successful - User: {customer['email']}")
            print_info(f"Is Admin: {customer.get('is_admin', False)}")
            return token
        else:
            error_msg = response.json().get('error', 'Unknown error')
            print_error(f"Login failed: {error_msg}")
            return None
    except Exception as e:
        print_error(f"Auth test failed: {e}")
        return None

def test_cart(token):
    """Test cart endpoints"""
    print_section("Testing Cart Endpoints")
    
    if not token:
        print_error("No token available for cart test")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Get cart
        response = requests.get(f"{BASE_URL}/cart", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Cart retrieved - Items: {data['item_count']}, Total: ₹{data['total']}")
        else:
            print_error(f"Failed to get cart: {response.status_code}")
    except Exception as e:
        print_error(f"Cart test failed: {e}")

def test_orders(token):
    """Test order endpoints"""
    print_section("Testing Order Endpoints")
    
    if not token:
        print_error("No token available for order test")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/orders", headers=headers)
        if response.status_code == 200:
            data = response.json()
            orders = data.get('orders', [])
            print_success(f"Orders retrieved - Total: {len(orders)}")
            if orders:
                order = orders[0]
                print_info(f"Sample order: #{order['order_id']} - ₹{order['total_amount']} ({order['order_status']})")
        else:
            print_error(f"Failed to get orders: {response.status_code}")
    except Exception as e:
        print_error(f"Order test failed: {e}")

def test_addresses(token):
    """Test address endpoints"""
    print_section("Testing Address Endpoints")
    
    if not token:
        print_error("No token available for address test")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/addresses", headers=headers)
        if response.status_code == 200:
            data = response.json()
            addresses = data.get('addresses', [])
            print_success(f"Addresses retrieved - Total: {len(addresses)}")
            if addresses:
                addr = addresses[0]
                print_info(f"Sample address: {addr.get('street_address')}, {addr.get('city')}")
        else:
            print_error(f"Failed to get addresses: {response.status_code}")
    except Exception as e:
        print_error(f"Address test failed: {e}")

def test_reviews():
    """Test review endpoints"""
    print_section("Testing Review Endpoints")
    
    try:
        response = requests.get(f"{BASE_URL}/reviews/product/1")
        if response.status_code == 200:
            data = response.json()
            reviews = data.get('reviews', [])
            print_success(f"Reviews retrieved - Total: {len(reviews)}")
        else:
            print_error(f"Failed to get reviews: {response.status_code}")
    except Exception as e:
        print_error(f"Review test failed: {e}")

def test_profile(token):
    """Test user profile endpoints"""
    print_section("Testing User Profile Endpoints")
    
    if not token:
        print_error("No token available for profile test")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Get profile
        response = requests.get(f"{BASE_URL}/profile", headers=headers)
        if response.status_code == 200:
            data = response.json()
            profile = data.get('profile', {})
            print_success(f"Profile retrieved - User: {profile.get('first_name')} {profile.get('last_name')}")
            
        # Get statistics
        response = requests.get(f"{BASE_URL}/profile/statistics", headers=headers)
        if response.status_code == 200:
            stats = response.json()
            print_success(f"Statistics retrieved")
            print_info(f"  Orders: {stats['total_orders']}")
            print_info(f"  Total Spent: ₹{stats['total_spent']}")
            print_info(f"  Reviews: {stats['total_reviews']}")
        else:
            print_error(f"Failed to get statistics: {response.status_code}")
    except Exception as e:
        print_error(f"Profile test failed: {e}")

def main():
    print(f"\n{BLUE}╔════════════════════════════════════════════════════════╗")
    print(f"║     ShopScale E-Commerce Platform - API Test Suite     ║")
    print(f"║                  {datetime.now().strftime('%Y-%m-%d %H:%M')}                    ║")
    print(f"╚════════════════════════════════════════════════════════╝{RESET}\n")
    
    print_info(f"Testing API at: {BASE_URL}\n")
    
    # Run tests
    if not test_health():
        print_error("\n❌ API is not running. Please start the backend server.")
        print_info("Run: python backend/app.py")
        return
    
    test_products()
    token = test_auth()
    test_cart(token)
    test_orders(token)
    test_addresses(token)
    test_reviews()
    test_profile(token)
    
    print_section("Test Summary")
    print_success("All endpoint tests completed!")
    print_info("Check individual results above for detailed status.")
    
    print(f"\n{BLUE}═══════════════════════════════════════════════════════{RESET}\n")

if __name__ == "__main__":
    main()
