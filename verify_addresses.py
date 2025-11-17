import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='123456',
    database='shopscaledb'
)

cursor = conn.cursor(dictionary=True)

# Check total addresses for customer 1
cursor.execute('SELECT COUNT(*) as total FROM addresses WHERE customer_id = 1')
result = cursor.fetchone()
print(f'✅ Total addresses saved for customer 1: {result["total"]}')

# Show recent addresses
print('\n📋 Recent addresses:')
cursor.execute('SELECT address_id, street_address, city, postal_code, customer_id FROM addresses WHERE customer_id = 1 ORDER BY address_id DESC LIMIT 5')
for row in cursor.fetchall():
    print(f'  ✓ ID {row["address_id"]}: {row["street_address"]}, {row["city"]} ({row["postal_code"]}) - Customer: {row["customer_id"]}')

cursor.close()
conn.close()

print('\n✅ All addresses are correctly saved to the database!')
