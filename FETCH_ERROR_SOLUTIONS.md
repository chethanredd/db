# Failed to Fetch - Complete Troubleshooting Guide

## Quick Diagnostics

When you see **"Failed to fetch"** error in the frontend, it means the browser **cannot reach the backend server**. Here's how to fix it:

---

## ✅ Step-by-Step Solution

### **Step 1: Check Backend Server Status**

#### Option A: Terminal Check
```powershell
# From c:\Users\gsche\OneDrive\Documents\db
cd backend
python app.py
```

**Expected output:**
```
* Running on http://127.0.0.1:5000
* WARNING: This is a development server. Do not use it in production deployment.
* Press CTRL+C to quit
```

#### Option B: Browser Health Check
Open this URL in your browser:
```
http://localhost:5000/api/health
```

You should see:
```json
{
  "status": "OK",
  "message": "ShopScale API is running",
  "database": "Connected"
}
```

---

### **Step 2: Check Database Connection**

```powershell
# Test MySQL connection
mysql -h localhost -u root -p123456 shopscaledb -e "SELECT 1;"
```

Expected: Shows a successful query result

---

### **Step 3: Check Browser Console for Detailed Error**

1. Open browser **Developer Tools** (F12)
2. Go to **Console** tab
3. Look for error messages like:
   - `net::ERR_CONNECTION_REFUSED` → Backend not running
   - `net::ERR_NAME_NOT_RESOLVED` → Wrong hostname
   - `net::ERR_CONNECTION_RESET` → Server crashed

---

### **Step 4: Check Network Tab**

1. Open **Network** tab in DevTools
2. Try to add an address
3. Look for the failed request (red color)
4. Click on it and check:
   - **Request URL**: Should be `http://localhost:5000/api/addresses`
   - **Status**: Should be 200, not "Failed"
   - **Headers**: Should have `Authorization: Bearer <token>`

---

## 🔴 Common "Failed to Fetch" Causes

### **Issue 1: Backend Server Not Running**

**Symptom:** 
- All network requests fail with "Failed to fetch"
- Browser console: `net::ERR_CONNECTION_REFUSED`

**Solution:**
```powershell
cd C:\Users\gsche\OneDrive\Documents\db\backend
python app.py
```

**Verify:** http://localhost:5000/api/health returns JSON

---

### **Issue 2: Wrong API URL in Frontend**

**Check in `AddressManager.jsx`:**
```javascript
const API_BASE_URL = 'http://localhost:5000/api';
```

**Should be exactly:**
- ✅ `http://localhost:5000/api` (with /api)
- ❌ `http://localhost:5000` (missing /api)
- ❌ `http://localhost:8000` (wrong port)
- ❌ `https://localhost:5000` (should be http, not https)

**Fix:**
```javascript
// In AddressManager.jsx, App.jsx
const API_BASE_URL = 'http://localhost:5000/api';
```

---

### **Issue 3: Missing or Invalid Auth Token**

**Symptom:**
- "Failed to fetch" when authenticated
- Browser console shows: `Authorization: undefined`

**Causes:**
1. Not logged in
2. Token expired
3. Token not saved to localStorage

**Solution:**

1. **Verify Login First:**
   ```
   Login button → Enter credentials → Check Console
   ```

2. **Check Token in Browser Console:**
   ```javascript
   localStorage.getItem('token')
   ```
   Should return a long JWT token string, not `null`

3. **Force Login Again:**
   - Click Logout
   - Click Login
   - Enter credentials
   - Try address save again

---

### **Issue 4: CORS (Cross-Origin Request Blocked)**

**Symptom:**
- Browser console CORS error
- Request shows "Failed" in Network tab

**Solution:**

Backend already has CORS enabled in `app.py`:
```python
from flask_cors import CORS
CORS(app)
```

If still failing, add explicit headers in `AddressManager.jsx`:
```javascript
const response = await fetch(`${API_BASE_URL}/addresses`, {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${authToken}`,
    'Content-Type': 'application/json'  // ← Add this line
  }
});
```

✅ **Already fixed in the updated AddressManager.jsx**

---

### **Issue 5: Database Connection Failed**

**Symptom:**
- Backend runs but returns error 500
- Console shows: "Database connection failed"

**Solution:**

Check MySQL is running:
```powershell
# Test MySQL
mysql -h localhost -u root -p123456 -e "USE shopscaledb; SELECT COUNT(*) as customers FROM customers;"
```

Expected: Returns a number

**If fails:**
1. Start MySQL: `net start MySQL80` (or MySQL57)
2. Check credentials in `.env`:
   ```
   DB_HOST=localhost
   DB_USER=root
   DB_PASSWORD=123456
   DB_NAME=shopscaledb
   DB_PORT=3306
   ```

---

## 📋 Full Testing Checklist

Before trying to save address, check ALL of these:

- [ ] **Backend Running?**
  ```powershell
  netstat -ano | findstr "5000"
  ```
  Should show Python process on port 5000

- [ ] **MySQL Running?**
  ```powershell
  netstat -ano | findstr "3306"
  ```
  Should show MySQL on port 3306

- [ ] **Logged In?**
  - Browser Console: `localStorage.getItem('token')` returns JWT

- [ ] **Correct API URL?**
  - Check `AddressManager.jsx` has `http://localhost:5000/api`

- [ ] **Network Request Succeeds?**
  - Open DevTools → Network tab
  - Try to save address
  - Check if POST to `/api/addresses` returns 201 status

- [ ] **Address Appears in List?**
  - After save succeeds, addresses list should update
  - Check browser console for logged addresses

---

## 🚀 Quick Start Test

### Fastest way to verify everything works:

```powershell
# Terminal 1: Start MySQL
net start MySQL80

# Terminal 2: Start Backend
cd C:\Users\gsche\OneDrive\Documents\db\backend
python app.py

# Terminal 3: Check health
curl http://localhost:5000/api/health

# Browser:
1. Go to http://localhost:3000 (or your frontend port)
2. Login with: rajesh.kumar@email.com / password123
3. Click "Addresses" button
4. Click "Add New Address"
5. Fill form:
   - Street: 123 Main St
   - City: Delhi
   - State: Delhi
   - Postal Code: 110001
6. Click "Save Address"
```

**Expected result:** Alert says "✅ Address added successfully!"

---

## 🔍 Debug Logging Guide

### Backend Debug Output

When running `python app.py`, you should see:

```
📦 Creating address for customer 1
📋 Address data: {'street_address': '123 Main St', ...}
💾 Inserting address: 123 Main St, Delhi, Delhi
✅ Address inserted with ID: 11
📍 Setting as shipping address for customer 1
✅ Updated shipping address 11
✅ Address creation complete. ID: 11
```

### Frontend Debug Output

Open Browser Console (F12 → Console):

```javascript
// You should see:
📤 Submitting to: http://localhost:5000/api/addresses
📋 Address data: {street_address: "123 Main St", ...}
🔑 Auth token present: Yes
📥 Response status: 201 Created
📥 Response body: {address_id: 11, message: "..."}
✅ Address created successfully: {address_id: 11, ...}
```

---

## ⚠️ Common Mistakes

| Mistake | Fix |
|---------|-----|
| Typo in API URL | Use exact URL: `http://localhost:5000/api` |
| Forgot to login | Login before accessing protected endpoints |
| Token expired | Login again to get new token |
| Backend not running | Run `python app.py` in backend folder |
| MySQL not running | Run `net start MySQL80` |
| .env file missing | Create with DB credentials |
| Port 5000 in use | Change port in app.py or kill existing process |

---

## 💡 Pro Tips

1. **Keep DevTools open** while testing (F12)
   - Watch Console for logs
   - Watch Network tab for requests

2. **Copy exact error messages** from alerts
   - They show what went wrong

3. **Check backend terminal** for server logs
   - They show why requests fail

4. **Use different browsers** if one fails
   - Rules out browser-specific issues

5. **Clear cache** if things are weird
   - Ctrl+Shift+Delete

---

## 🆘 Still Getting "Failed to Fetch"?

Run this diagnostic:

```powershell
# Check what's listening on port 5000
netstat -ano | findstr "5000"

# Check process details
tasklist | findstr "python"

# Kill existing Python process if stuck
taskkill /PID <PID> /F

# Check MySQL
netstat -ano | findstr "3306"

# Test backend directly
curl -X GET http://localhost:5000/api/health -v

# Test auth
curl -X POST http://localhost:5000/api/auth/login `
  -H "Content-Type: application/json" `
  -d '{"email":"rajesh.kumar@email.com","password":"password123"}' `
  -v
```

---

## 📞 Quick Reference URLs

| Component | URL | Expected |
|-----------|-----|----------|
| Health Check | http://localhost:5000/api/health | JSON with status OK |
| Login | POST http://localhost:5000/api/auth/login | Returns JWT token |
| Get Addresses | GET http://localhost:5000/api/addresses | Returns address list |
| Save Address | POST http://localhost:5000/api/addresses | Returns address_id |
| Frontend | http://localhost:3000 | React app loads |
| Database | localhost:3306 | MySQL runs |

---

## ✅ Success Indicators

When everything is working:

- ✅ Backend runs without errors
- ✅ `http://localhost:5000/api/health` returns JSON
- ✅ Login succeeds and saves token to localStorage
- ✅ Address save shows success alert
- ✅ New address appears in address list
- ✅ Browser console shows ✅ messages, not ❌

---

Need help? Check the console logs - they'll tell you exactly what's wrong!
