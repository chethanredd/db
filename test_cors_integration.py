#!/usr/bin/env python3
"""
Integration test to verify frontend-backend CORS communication is working
"""
import requests
import json
from datetime import datetime
import sys

def test_cors_integration():
    """Test CORS configuration and basic API functionality"""
    
    print("\n" + "="*70)
    print("INTEGRATION TEST: Frontend-Backend CORS Communication")
    print("="*70)
    
    base_url = "http://localhost:5000/api"
    frontend_origin = "http://localhost:3000"
    
    # Test 1: Test preflight request
    print("\n[TEST 1] Preflight Request (OPTIONS)")
    print("-" * 70)
    try:
        response = requests.options(
            f"{base_url}/addresses/",
            headers={
                'Origin': frontend_origin,
                'Access-Control-Request-Method': 'GET',
                'Access-Control-Request-Headers': 'content-type,authorization'
            }
        )
        
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
            'Access-Control-Allow-Credentials': response.headers.get('Access-Control-Allow-Credentials'),
            'Access-Control-Max-Age': response.headers.get('Access-Control-Max-Age')
        }
        
        print(f"Status: {response.status_code}")
        print("CORS Headers:")
        for key, value in cors_headers.items():
            if value:
                print(f"  {key}: {value}")
        
        if response.status_code == 200 and cors_headers['Access-Control-Allow-Origin'] == frontend_origin:
            print("✅ PASS: Preflight request successful with correct origin")
        else:
            print("❌ FAIL: Preflight request did not return expected headers")
            return False
    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        return False
    
    # Test 2: Get products endpoint (no auth required)
    print("\n[TEST 2] GET /api/products (No Authentication)")
    print("-" * 70)
    try:
        response = requests.get(
            f"{base_url}/products",
            headers={
                'Origin': frontend_origin,
                'Content-Type': 'application/json'
            }
        )
        
        print(f"Status: {response.status_code}")
        data = response.json()
        
        if response.status_code == 200 and 'products' in data:
            print(f"✅ PASS: Fetched {len(data['products'])} products")
        else:
            print(f"❌ FAIL: Unexpected response structure: {data}")
            return False
    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        return False
    
    # Test 3: Login endpoint (test unauthenticated POST with CORS)
    print("\n[TEST 3] POST /api/auth/login (No Authentication)")
    print("-" * 70)
    try:
        response = requests.post(
            f"{base_url}/auth/login",
            headers={
                'Origin': frontend_origin,
                'Content-Type': 'application/json'
            },
            json={'email': 'test@test.com', 'password': 'test123'}
        )
        
        print(f"Status: {response.status_code}")
        
        # Check CORS headers are present
        has_cors = response.headers.get('Access-Control-Allow-Origin') == frontend_origin
        
        if has_cors:
            print("✅ PASS: CORS headers present for POST request")
        else:
            print("❌ FAIL: Missing CORS headers on POST response")
            return False
    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        return False
    
    # Test 4: Test authenticated endpoint with token
    print("\n[TEST 4] GET /api/addresses (With Authentication)")
    print("-" * 70)
    test_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjdXN0b21lcl9pZCI6MSwiZW1haWwiOiJ0ZXN0QHRlc3QuY29tIn0.M0EcXxFXo0Z8yv9C2-3Kv-4Kv9C2-3Kv-4Kv9C2"
    try:
        response = requests.get(
            f"{base_url}/addresses/",
            headers={
                'Origin': frontend_origin,
                'Authorization': f'Bearer {test_token}',
                'Content-Type': 'application/json'
            }
        )
        
        print(f"Status: {response.status_code}")
        
        # Check CORS headers
        has_cors = response.headers.get('Access-Control-Allow-Origin') == frontend_origin
        has_credentials = response.headers.get('Access-Control-Allow-Credentials') == 'true'
        
        if response.status_code == 401:  # Token invalid is expected
            print("Token Status: Invalid (expected for test token)")
            if has_cors and has_credentials:
                print("✅ PASS: CORS headers correct for authenticated endpoints")
            else:
                print("❌ FAIL: Missing CORS headers or credentials flag")
                return False
        elif response.status_code == 200:
            print("✅ PASS: Request successful")
        else:
            print(f"Status code: {response.status_code}")
    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        return False
    
    # Test 5: Verify all required origins are allowed
    print("\n[TEST 5] Multiple Frontend Origins")
    print("-" * 70)
    test_origins = [
        'http://localhost:3000',
        'http://127.0.0.1:3000',
        'http://localhost:5173',
        'http://127.0.0.1:5173'
    ]
    
    all_origins_ok = True
    for origin in test_origins:
        try:
            response = requests.options(
                f"{base_url}/addresses/",
                headers={
                    'Origin': origin,
                    'Access-Control-Request-Method': 'GET',
                    'Access-Control-Request-Headers': 'content-type,authorization'
                }
            )
            
            if response.headers.get('Access-Control-Allow-Origin') == origin:
                print(f"  ✅ {origin}")
            else:
                print(f"  ❌ {origin} - Not allowed")
                all_origins_ok = False
        except Exception as e:
            print(f"  ❌ {origin} - Error: {str(e)}")
            all_origins_ok = False
    
    if all_origins_ok:
        print("✅ PASS: All frontend origins allowed")
    else:
        return False
    
    print("\n" + "="*70)
    print("✅ ALL TESTS PASSED - CORS is properly configured!")
    print("="*70)
    print("\nFrontend on http://localhost:3000 can now communicate with")
    print("Backend on http://localhost:5000")
    print("\n")
    
    return True

if __name__ == "__main__":
    success = test_cors_integration()
    sys.exit(0 if success else 1)
