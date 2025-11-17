#!/usr/bin/env python3
"""
Test the address API endpoints
"""

import requests
import json

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

try:
    print_section("STEP 1: Login")
    login_response = requests.post('http://localhost:5000/api/auth/login', json={
        'email': 'rajesh.kumar@email.com',
        'password': 'password123'
    })
    
    print(f"Status: {login_response.status_code}")
    
    if login_response.status_code == 200:
        print("✅ Login successful")
        data = login_response.json()
        token = data['token']
        customer_id = data['customer']['customer_id']
        print(f"Token: {token[:50]}...")
        print(f"Customer ID: {customer_id}")
    else:
        print(f"❌ Login failed")
        print(f"Response: {login_response.text}")
        exit(1)
    
    headers = {'Authorization': f'Bearer {token}'}
    
    print_section("STEP 2: GET Addresses (before create)")
    get_response = requests.get('http://localhost:5000/api/addresses', headers=headers)
    print(f"Status: {get_response.status_code}")
    if get_response.status_code == 200:
        addresses = get_response.json()['addresses']
        print(f"✅ Found {len(addresses)} addresses")
        for i, addr in enumerate(addresses, 1):
            print(f"  {i}. {addr.get('street_address')}, {addr.get('city')}")
    else:
        print(f"❌ Failed: {get_response.text}")
    
    print_section("STEP 3: CREATE New Address")
    address_data = {
        'street_address': '999 Test Street',
        'city': 'Test City',
        'state': 'Test State',
        'postal_code': '999999',
        'country': 'India',
        'address_type': 'both'
    }
    print(f"Creating address:")
    print(json.dumps(address_data, indent=2))
    
    post_response = requests.post('http://localhost:5000/api/addresses',
                                 headers=headers,
                                 json=address_data)
    print(f"\nStatus: {post_response.status_code}")
    print(f"Response: {json.dumps(post_response.json(), indent=2)}")
    
    if post_response.status_code == 201:
        address_id = post_response.json()['address_id']
        print(f"✅ Address created with ID: {address_id}")
    else:
        print(f"❌ Failed to create address")
    
    print_section("STEP 4: GET Addresses (after create)")
    get_response = requests.get('http://localhost:5000/api/addresses', headers=headers)
    print(f"Status: {get_response.status_code}")
    if get_response.status_code == 200:
        addresses = get_response.json()['addresses']
        print(f"✅ Found {len(addresses)} addresses")
        for i, addr in enumerate(addresses, 1):
            print(f"  {i}. {addr.get('street_address')}, {addr.get('city')}")
    else:
        print(f"❌ Failed: {get_response.text}")
    
    print_section("✅ ALL TESTS PASSED")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
