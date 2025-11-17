#!/usr/bin/env python3
"""
Script to fix admin password in the database.
This updates the admin@shopscale.com account with a proper bcrypt hash.
"""

import mysql.connector
import bcrypt

# Database configuration
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "123456"
DB_NAME = "shopscaledb"

# Admin credentials
ADMIN_EMAIL = "admin@shopscale.com"
ADMIN_PASSWORD = "password123"

try:
    # Connect to database
    conn = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    
    cursor = conn.cursor()
    
    # Generate bcrypt hash for password
    password_hash = bcrypt.hashpw(ADMIN_PASSWORD.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    print(f"Fixing admin password for: {ADMIN_EMAIL}")
    print(f"New hash: {password_hash}")
    
    # Update admin password
    cursor.execute(
        "UPDATE customers SET password_hash = %s WHERE email = %s",
        (password_hash, ADMIN_EMAIL)
    )
    
    conn.commit()
    
    # Verify update
    cursor.execute("SELECT email, password_hash FROM customers WHERE email = %s", (ADMIN_EMAIL,))
    result = cursor.fetchone()
    
    if result:
        print(f"✅ Admin password updated successfully!")
        print(f"Email: {result[0]}")
        print(f"Hash: {result[1][:50]}...")
        print(f"\nYou can now login with:")
        print(f"  Email: {ADMIN_EMAIL}")
        print(f"  Password: {ADMIN_PASSWORD}")
    else:
        print(f"❌ Admin user not found!")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
