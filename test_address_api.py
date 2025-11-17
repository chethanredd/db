#!/usr/bin/env python3
"""
Test script for Address API
Run this after logging in to test address creation and retrieval
"""

import requests
import json
import sys

# Configuration
API_BASE_URL = 'http://localhost:5000/api'
EMAIL = 'rajesh.kumar@email.com'
PASSWORD = 'password123'

class AddressAPITester:
    def __init__(self):
        self.token = None
        self.customer_id = None
        self.session = requests.Session()
    
    def login(self):
        """Login and get JWT token"""
        print("\n🔐 Logging in...")
        try:
            response = requests.post(
                f'{API_BASE_URL}/auth/login',
                json={'email': EMAIL, 'password': PASSWORD}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data['token']
                self.customer_id = data['customer']['customer_id']
                print(f"✅ Login successful!")
                print(f"   Token: {self.token[:50]}...")
                print(f"   Customer ID: {self.customer_id}")
                return True
            else:
                print(f"❌ Login failed: {response.json()}")
                return False
        except Exception as e:
            print(f"❌ Error logging in: {e}")
            return False
    
    def get_headers(self):
        """Get headers with auth token"""
        return {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
    
    def create_address(self, street, city, state, postal_code):
        """Create a new address"""
        print(f"\n📍 Creating address...")
        try:
            payload = {
                'street_address': street,
                'city': city,
                'state': state,
                'postal_code': postal_code,
                'country': 'India',
                'set_as_shipping': True,
                'set_as_billing': True
            }
            
            print(f"   Payload: {json.dumps(payload, indent=2)}")
            
            response = requests.post(
                f'{API_BASE_URL}/addresses',
                headers=self.get_headers(),
                json=payload
            )
            
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
            
            if response.status_code == 201:
                data = response.json()
                print(f"✅ Address created successfully!")
                print(f"   Address ID: {data['address_id']}")
                return data['address_id']
            else:
                print(f"❌ Failed to create address")
                return None
        except Exception as e:
            print(f"❌ Error creating address: {e}")
            return None
    
    def get_addresses(self):
        """Get all addresses for customer"""
        print(f"\n📋 Fetching addresses...")
        try:
            response = requests.get(
                f'{API_BASE_URL}/addresses',
                headers=self.get_headers()
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                addresses = data['addresses']
                
                if addresses:
                    print(f"✅ Found {len(addresses)} address(es):")
                    for i, addr in enumerate(addresses, 1):
                        print(f"\n   Address {i}:")
                        print(f"      ID: {addr['address_id']}")
                        print(f"      Street: {addr['street_address']}")
                        print(f"      City: {addr['city']}")
                        print(f"      State: {addr['state']}")
                        print(f"      Postal: {addr['postal_code']}")
                        print(f"      Country: {addr['country']}")
                        print(f"      Type: {addr['address_type']}")
                        print(f"      Created: {addr['created_at']}")
                    return addresses
                else:
                    print(f"ℹ️  No addresses found")
                    return []
            else:
                print(f"❌ Failed to fetch addresses: {response.json()}")
                return []
        except Exception as e:
            print(f"❌ Error fetching addresses: {e}")
            return []
    
    def delete_address(self, address_id):
        """Delete an address"""
        print(f"\n🗑️  Deleting address {address_id}...")
        try:
            response = requests.delete(
                f'{API_BASE_URL}/addresses/{address_id}',
                headers=self.get_headers()
            )
            
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
            
            if response.status_code == 200:
                print(f"✅ Address deleted successfully!")
                return True
            else:
                print(f"❌ Failed to delete address")
                return False
        except Exception as e:
            print(f"❌ Error deleting address: {e}")
            return False
    
    def run_full_test(self):
        """Run complete address API test"""
        print("=" * 60)
        print("🧪 ADDRESS API TEST SUITE")
        print("=" * 60)
        
        # Step 1: Login
        if not self.login():
            print("\n❌ Cannot proceed without login")
            return False
        
        # Step 2: Get initial addresses
        initial_addresses = self.get_addresses()
        initial_count = len(initial_addresses)
        print(f"\n📊 Initial address count: {initial_count}")
        
        # Step 3: Create test address
        new_address_id = self.create_address(
            street='456 Test Avenue',
            city='Pune',
            state='Maharashtra',
            postal_code='411001'
        )
        
        if not new_address_id:
            print("\n❌ Failed to create test address")
            return False
        
        # Step 4: Get addresses after creation
        updated_addresses = self.get_addresses()
        updated_count = len(updated_addresses)
        print(f"\n📊 Updated address count: {updated_count}")
        
        # Verify
        if updated_count > initial_count:
            print(f"\n✅ VERIFICATION PASSED: Address count increased from {initial_count} to {updated_count}")
        else:
            print(f"\n❌ VERIFICATION FAILED: Address count did not increase")
            return False
        
        # Step 5: Delete test address
        if self.delete_address(new_address_id):
            final_addresses = self.get_addresses()
            final_count = len(final_addresses)
            print(f"\n📊 Final address count: {final_count}")
            
            if final_count == initial_count:
                print(f"\n✅ VERIFICATION PASSED: Address count returned to {initial_count}")
            else:
                print(f"\n❌ VERIFICATION FAILED: Address count is {final_count}, expected {initial_count}")
        
        print("\n" + "=" * 60)
        print("✅ TEST COMPLETE")
        print("=" * 60)
        return True

def main():
    """Main test runner"""
    print("""
    🧪 ADDRESS API TESTER
    
    This script will test the Address API by:
    1. Logging in with test account
    2. Getting initial addresses
    3. Creating a new address
    4. Verifying address appears in list
    5. Deleting the test address
    6. Verifying address is removed
    
    Test account: rajesh.kumar@email.com / password123
    API URL: http://localhost:5000/api
    
    Make sure:
    - Backend is running (python backend/app.py)
    - MySQL is running
    - Database.sql has been imported
    
    """)
    
    try:
        tester = AddressAPITester()
        success = tester.run_full_test()
        
        if success:
            print("\n🎉 All tests passed!")
            sys.exit(0)
        else:
            print("\n⚠️  Some tests failed")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
