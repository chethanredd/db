import requests
import json

# First, login to get a token
print("🔐 Logging in...")
login_response = requests.post(
    'http://localhost:5000/api/auth/login',
    json={'email': 'rajesh.kumar@email.com', 'password': 'password123'}
)

print("Login Status:", login_response.status_code)
login_data = login_response.json()

if login_response.status_code == 200:
    token = login_data.get('token')
    print("✅ Login successful")
    print("Token:", token[:20] + "...")
    
    # Now try to create an address
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    address_data = {
        'street_address': '999 Test Street',
        'city': 'Test City',
        'state': 'Test State',
        'postal_code': '999999',
        'country': 'India',
        'address_type': 'both'
    }
    
    print("\n📤 Sending address data:", json.dumps(address_data, indent=2))
    
    response = requests.post(
        'http://localhost:5000/api/addresses',
        headers=headers,
        json=address_data
    )
    
    print("\n📥 Response Status:", response.status_code)
    print("📥 Response:", json.dumps(response.json(), indent=2))
    
    # Now try to fetch addresses
    print("\n📦 Fetching addresses...")
    fetch_response = requests.get(
        'http://localhost:5000/api/addresses',
        headers=headers
    )
    
    print("Fetch Status:", fetch_response.status_code)
    fetch_data = fetch_response.json()
    print("Addresses:", json.dumps(fetch_data, indent=2))
else:
    print("❌ Login failed:", login_data)
