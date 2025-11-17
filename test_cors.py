#!/usr/bin/env python3
import requests
import json

# Test the CORS headers and OPTIONS preflight
print("=" * 60)
print("TESTING CORS CONFIGURATION")
print("=" * 60)

# First test OPTIONS request (preflight)
print("\n1. Testing OPTIONS preflight request:")
options_resp = requests.options(
    'http://localhost:5000/api/addresses/',
    headers={
        'Origin': 'http://localhost:3000',
        'Access-Control-Request-Method': 'GET',
        'Access-Control-Request-Headers': 'content-type,authorization'
    }
)
print(f"   Status: {options_resp.status_code}")
print(f"   Response Headers:")
for key, value in options_resp.headers.items():
    if 'access-control' in key.lower() or 'access' in key.lower():
        print(f"     {key}: {value}")

# Now test actual GET request with token
print("\n2. Testing GET request with token (will fail without token, but tests CORS):")
test_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjdXN0b21lcl9pZCI6MSwiZW1haWwiOiJ0ZXN0QHRlc3QuY29tIn0.M0EcXxFXo0Z8yv9C2-3Kv-4Kv9C2-3Kv-4Kv9C2'
get_resp = requests.get(
    'http://localhost:5000/api/addresses/',
    headers={
        'Origin': 'http://localhost:3000',
        'Authorization': f'Bearer {test_token}',
        'Content-Type': 'application/json'
    }
)
print(f"   Status: {get_resp.status_code}")
print(f"   Response Headers:")
for key, value in get_resp.headers.items():
    if 'access-control' in key.lower() or 'access' in key.lower():
        print(f"     {key}: {value}")
print(f"   Body: {get_resp.text[:200]}")

print("\n3. Testing POST request (create address):")
post_resp = requests.post(
    'http://localhost:5000/api/addresses/',
    headers={
        'Origin': 'http://localhost:3000',
        'Authorization': f'Bearer {test_token}',
        'Content-Type': 'application/json'
    },
    json={'street_address': '123 Main', 'city': 'NYC', 'state': 'NY', 'postal_code': '10001'}
)
print(f"   Status: {post_resp.status_code}")
print(f"   Response Headers:")
for key, value in post_resp.headers.items():
    if 'access-control' in key.lower() or 'access' in key.lower():
        print(f"     {key}: {value}")

print("\n" + "=" * 60)
print("CORS TEST COMPLETE")
print("=" * 60)
