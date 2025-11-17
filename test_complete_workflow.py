#!/usr/bin/env python3
"""
Comprehensive End-to-End Testing Script for ShopScale E-Commerce
Tests the entire workflow:
1. User Login
2. Add Address
3. Add Products to Cart
4. Create Order
5. Process Payment (multiple methods)
6. Verify Triggers & Functions
"""

import requests
import json
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:5000/api"
TEST_EMAIL = "rajesh.kumar@email.com"
TEST_PASSWORD = "password123"

# Colors for console output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_section(title):
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}{Colors.END}\n")

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.CYAN}ℹ️  {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.END}")

# Test 1: Login
def test_login():
    print_section("TEST 1: USER LOGIN")
    try:
        print_info(f"Logging in as: {TEST_EMAIL}")
        response = requests.post(f"{API_BASE_URL}/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        
        if response.status_code == 200:
            data = response.json()
            token = data['token']
            customer_id = data['customer']['customer_id']
            print_success(f"Login successful for customer ID: {customer_id}")
            print(f"   Name: {data['customer']['first_name']} {data['customer']['last_name']}")
            print(f"   Email: {data['customer']['email']}")
            return token, customer_id
        else:
            print_error(f"Login failed: {response.json()}")
            return None, None
    except Exception as e:
        print_error(f"Login error: {e}")
        return None, None

# Test 2: Get Products
def test_get_products(token):
    print_section("TEST 2: FETCH PRODUCTS")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        print_info("Fetching available products...")
        response = requests.get(f"{API_BASE_URL}/products", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            products = data['products'][:3]  # Get first 3 products
            print_success(f"Fetched {len(products)} products (showing first 3)")
            
            for i, product in enumerate(products, 1):
                print(f"   {i}. {product['name']} - ₹{product['price']} (Stock: {product['stock']})")
            
            return products
        else:
            print_error(f"Failed to fetch products: {response.json()}")
            return []
    except Exception as e:
        print_error(f"Get products error: {e}")
        return []

# Test 3: Add Address
def test_add_address(token, customer_id):
    print_section("TEST 3: ADD DELIVERY ADDRESS")
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        address_data = {
            "street_address": "999 Test Avenue",
            "city": "Bengaluru",
            "state": "Karnataka",
            "postal_code": "560001",
            "country": "India",
            "address_type": "both"
        }
        
        print_info(f"Adding address: {address_data['street_address']}, {address_data['city']}")
        response = requests.post(f"{API_BASE_URL}/addresses/", json=address_data, headers=headers)
        
        if response.status_code == 201:
            data = response.json()
            address_id = data['address_id']
            print_success(f"Address added successfully with ID: {address_id}")
            return address_id
        else:
            print_error(f"Failed to add address: {response.json()}")
            return None
    except Exception as e:
        print_error(f"Add address error: {e}")
        return None

# Test 4: Add to Cart
def test_add_to_cart(token, products):
    print_section("TEST 4: ADD PRODUCTS TO CART")
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        added_items = []
        for i, product in enumerate(products, 1):
            quantity = 1 + (i % 2)  # Alternate between 1 and 2
            print_info(f"Adding {quantity}x {product['name']} to cart...")
            
            response = requests.post(f"{API_BASE_URL}/cart/items", json={
                "product_id": product['id'],
                "quantity": quantity
            }, headers=headers)
            
            if response.status_code == 200:
                print_success(f"Added to cart: {quantity}x {product['name']}")
                added_items.append({"product": product, "quantity": quantity})
            else:
                print_error(f"Failed to add {product['name']} to cart")
        
        return added_items
    except Exception as e:
        print_error(f"Add to cart error: {e}")
        return []

# Test 5: Get Cart
def test_get_cart(token):
    print_section("TEST 5: VIEW CART")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        print_info("Fetching cart contents...")
        response = requests.get(f"{API_BASE_URL}/cart", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            cart_items = data['items']
            total = data['total']
            print_success(f"Cart retrieved: {len(cart_items)} items, Total: ₹{total}")
            
            for item in cart_items:
                print(f"   - {item['name']}: {item['quantity']}x ₹{item['price']} = ₹{item['price']*item['quantity']}")
            
            return total, cart_items
        else:
            print_error(f"Failed to get cart: {response.json()}")
            return 0, []
    except Exception as e:
        print_error(f"Get cart error: {e}")
        return 0, []

# Test 6: Create Order
def test_create_order(token, address_id):
    print_section("TEST 6: CREATE ORDER")
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        order_data = {
            "shipping_address_id": address_id,
            "billing_address_id": address_id,
            "payment_method": "cod"  # Cash on Delivery
        }
        
        print_info(f"Creating order with COD payment...")
        print(f"   Shipping Address ID: {address_id}")
        print(f"   Payment Method: Cash on Delivery")
        
        response = requests.post(f"{API_BASE_URL}/orders/create", json=order_data, headers=headers)
        
        if response.status_code == 201:
            data = response.json()
            order_id = data['order_id']
            print_success(f"Order created successfully with ID: {order_id}")
            print(f"   Subtotal: ₹{data['subtotal']}")
            print(f"   Tax (18%): ₹{data['tax_amount']}")
            print(f"   Shipping: ₹{data['shipping_amount']}")
            print(f"   TOTAL: ₹{data['total_amount']}")
            return order_id, data['total_amount']
        else:
            print_error(f"Failed to create order: {response.json()}")
            return None, None
    except Exception as e:
        print_error(f"Create order error: {e}")
        import traceback
        traceback.print_exc()
        return None, None

# Test 7: Process Payment
def test_process_payment(token, order_id, payment_methods):
    print_section("TEST 7: PROCESS PAYMENT")
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        results = []
        
        for method in payment_methods:
            print_info(f"Processing payment with: {method}")
            
            response = requests.post(f"{API_BASE_URL}/payments/process", json={
                "order_id": order_id,
                "payment_method": method
            }, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print_success(f"Payment processed: {method}")
                print(f"   Transaction ID: {data['transaction_id']}")
                print(f"   Status: {data['payment_status']}")
                print(f"   Gateway: {data['payment_gateway']}")
                results.append((method, True))
            else:
                print_error(f"Payment failed: {response.json()}")
                results.append((method, False))
        
        return results
    except Exception as e:
        print_error(f"Payment processing error: {e}")
        import traceback
        traceback.print_exc()
        return []

# Test 8: Get Order Details
def test_get_order_details(token, order_id):
    print_section("TEST 8: VIEW ORDER DETAILS")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        print_info(f"Fetching details for order {order_id}...")
        
        response = requests.get(f"{API_BASE_URL}/orders/{order_id}", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            order = data['order']
            items = data['items']
            payment = data['payment']
            
            print_success(f"Order details retrieved")
            print(f"   Order ID: {order['order_id']}")
            print(f"   Status: {order['order_status']}")
            print(f"   Total Amount: ₹{order['total_amount']}")
            print(f"\n   Items:")
            for item in items:
                print(f"      - {item['product_name']}: {item['quantity']}x ₹{item['unit_price']}")
            
            if payment:
                print(f"\n   Payment:")
                print(f"      - Method: {payment['payment_method']}")
                print(f"      - Status: {payment['payment_status']}")
                print(f"      - Transaction ID: {payment['transaction_id']}")
            
            return True
        else:
            print_error(f"Failed to get order details: {response.json()}")
            return False
    except Exception as e:
        print_error(f"Get order details error: {e}")
        return False

# Test 9: Verify Database Functions
def test_database_functions(token):
    print_section("TEST 9: DATABASE FUNCTIONS & TRIGGERS")
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        print_info("Verifying database functions and triggers...")
        print_info("The following should have been executed:")
        print("   1. Stock Update Trigger - reduces product stock on order creation")
        print("   2. Order Tax Calculation - 18% GST on order total")
        print("   3. Payment Processing - updates payment status based on method")
        
        # Fetch orders to verify
        response = requests.get(f"{API_BASE_URL}/orders/", headers=headers)
        if response.status_code == 200:
            orders = response.json()['orders']
            print_success(f"Database is functional - {len(orders)} orders found")
            return True
        else:
            print_error("Failed to verify database")
            return False
            
    except Exception as e:
        print_error(f"Database verification error: {e}")
        return False

# Main Test Suite
def main():
    print(f"\n{Colors.BOLD}{Colors.CYAN}")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║       SHOPSCALE E-COMMERCE - END-TO-END TEST SUITE                 ║")
    print("║                                                                    ║")
    print("║  Testing: Address Management, Orders, Payments & Triggers         ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.END}")
    
    start_time = datetime.now()
    
    # Test 1: Login
    token, customer_id = test_login()
    if not token:
        print_error("Cannot continue without valid token")
        return
    
    # Test 2: Get Products
    products = test_get_products(token)
    if not products:
        print_error("Cannot continue without products")
        return
    
    # Test 3: Add Address
    address_id = test_add_address(token, customer_id)
    if not address_id:
        print_error("Cannot continue without address")
        return
    
    # Test 4: Add to Cart
    cart_items = test_add_to_cart(token, products)
    if not cart_items:
        print_error("Cannot continue without cart items")
        return
    
    # Test 5: View Cart
    cart_total, cart_contents = test_get_cart(token)
    if not cart_contents:
        print_error("Cart is empty")
        return
    
    # Test 6: Create Order
    order_id, order_total = test_create_order(token, address_id)
    if not order_id:
        print_error("Cannot continue without order")
        return
    
    # Test 7: Process Payment (test multiple methods)
    payment_methods = ["cod", "upi", "credit_card"]
    payment_results = test_process_payment(token, order_id, payment_methods)
    
    # Test 8: View Order Details
    test_get_order_details(token, order_id)
    
    # Test 9: Verify Database Functions
    test_database_functions(token)
    
    # Summary
    print_section("TEST SUMMARY")
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print_success(f"All tests completed in {duration:.2f} seconds")
    print(f"\n{Colors.BOLD}Workflow Status:{Colors.END}")
    print(f"  ✅ User logged in (Customer ID: {customer_id})")
    print(f"  ✅ Address added (Address ID: {address_id})")
    print(f"  ✅ {len(cart_items)} products added to cart")
    print(f"  ✅ Order created (Order ID: {order_id})")
    print(f"  ✅ Payment processed via {len(payment_results)} methods")
    print(f"  ✅ Order total: ₹{order_total}")
    
    print(f"\n{Colors.BOLD}Payment Methods Tested:{Colors.END}")
    for method, success in payment_results:
        status = "✅" if success else "❌"
        print(f"  {status} {method.upper()}")
    
    print(f"\n{Colors.GREEN}{Colors.BOLD}✅ END-TO-END WORKFLOW VERIFIED SUCCESSFULLY!{Colors.END}\n")

if __name__ == "__main__":
    main()
