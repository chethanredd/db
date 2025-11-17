#!/usr/bin/env python3
"""
Fix password hashes in the database
This script creates proper bcrypt hashes for testing
"""

import bcrypt
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

# Generate a fresh bcrypt hash for "password123"
password = "password123"
salt = bcrypt.gensalt()
hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

print(f"Original password: {password}")
print(f"Generated hash: {hashed_password}")
print(f"Hash length: {len(hashed_password)}")

# Verify the hash works
is_valid = bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
print(f"Hash verification: {'✅ PASS' if is_valid else '❌ FAIL'}")

# Connect to database and update
try:
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='123456',
        database='shopscaledb'
    )
    cursor = connection.cursor()
    
    # Update all customer passwords
    cursor.execute(
        "UPDATE customers SET password_hash = %s WHERE email IN (%s, %s, %s, %s, %s, %s)",
        (
            hashed_password,
            'rajesh.kumar@email.com',
            'priya.sharma@email.com',
            'amit.singh@email.com',
            'sneha.patel@email.com',
            'admin@shopscale.com',
            'arjun.joshi@email.com'
        )
    )
    connection.commit()
    
    print(f"\n✅ Updated {cursor.rowcount} records in database")
    
    # Verify the update
    cursor.execute('SELECT email, password_hash FROM customers WHERE email = %s', ('rajesh.kumar@email.com',))
    result = cursor.fetchone()
    if result:
        print(f"\n✅ Database verification:")
        print(f"   Email: {result[0]}")
        print(f"   Hash: {result[1][:30]}...")
        
        # Test the hash
        is_valid_db = bcrypt.checkpw('password123'.encode('utf-8'), result[1].encode('utf-8'))
        print(f"   Verification: {'✅ PASS' if is_valid_db else '❌ FAIL'}")
    
    cursor.close()
    connection.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
