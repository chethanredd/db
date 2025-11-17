# 🔴 "Failed to Fetch" - Quick Fix Checklist

## 30 Second Quick Fix

```powershell
# Terminal 1: Start MySQL
net start MySQL80

# Terminal 2: Start Backend
cd C:\Users\gsche\OneDrive\Documents\db\backend
python app.py

# Terminal 3: Check if working
curl http://localhost:5000/api/health
```

If you see JSON response with `"status": "OK"` → Backend is working ✅

---

## Common Causes & Solutions

### ❌ Error: "Failed to fetch"

| Cause | Fix |
|-------|-----|
| Backend not running | `cd backend && python app.py` |
| MySQL not running | `net start MySQL80` |
| Wrong API URL | Check URL is `http://localhost:5000/api` |
| Firewall blocking port 5000 | Allow port 5000 in firewall |
| Token missing | Login again to get new token |
| Token expired | Logout → Login again |
| CORS error | Already fixed in code |

---

## Browser Console Debug

Press **F12** in browser → **Console** tab

### Good Logs (Everything Works)
```
📤 Submitting to: http://localhost:5000/api/addresses
🔑 Auth token present: Yes
📥 Response status: 201 Created
✅ Address created successfully
```

### Bad Logs (Something's Wrong)
```
🔴 Network error
Error: Failed to fetch
```

**Solution:** Check if backend is running!

---

## Test Commands

```powershell
# Check if backend is running on port 5000
netstat -ano | findstr "5000"

# Check if MySQL is running
netstat -ano | findstr "3306"

# Test backend directly
curl http://localhost:5000/api/health

# Force-kill stuck Python process
taskkill /PID 1234 /F

# Show all Python processes
tasklist | findstr "python"
```

---

## Before You Test Anything

Make sure ALL of these are True:

- [ ] MySQL running: `net start MySQL80`
- [ ] Backend running: `python app.py` (shows `Running on http://127.0.0.1:5000`)
- [ ] Browser can reach backend: http://localhost:5000/api/health shows JSON
- [ ] Logged in: Check console → `localStorage.getItem('token')`
- [ ] Token exists: Should be a long string starting with `ey...`

---

## Files Modified

| File | Changes |
|------|---------|
| `frontend/src/AddressManager.jsx` | ✅ Added Content-Type, logging, better errors |
| `frontend/src/Checkout.jsx` | ✅ Added logging, error detection, friendly messages |
| `frontend/src/OrderHistory.jsx` | ✅ Added headers, logging, error handling |
| `frontend/src/ReviewSystem.jsx` | ✅ Added logging, error messages, debugging |
| `frontend/src/App.jsx` | ✅ Added logging for product fetches |
| `backend/addresses.py` | ✅ Simplified query, added logging |

---

## What Changed

### Frontend
- ✅ All fetch requests now have `Content-Type: application/json` header
- ✅ All requests log to browser console with emojis
- ✅ All errors show helpful user-friendly messages
- ✅ "Failed to fetch" shows steps to fix connection issues

### Backend  
- ✅ Address query simplified from complex UNION to simple IN query
- ✅ All operations log with emojis for easy scanning
- ✅ Better error messages returned to frontend

---

## If Still Getting Error

### Step 1: Open Console (F12)
What do you see?

**A) "net::ERR_CONNECTION_REFUSED"** → Backend not running
```powershell
python backend/app.py
```

**B) "🔴 Network error: Failed to fetch"** → Connection problem
```powershell
# Test backend health
curl http://localhost:5000/api/health
# Should return JSON with "status": "OK"
```

**C) "❌ Server error: ..."** → Backend returned error
Check backend console for error logs (marked with ❌ or 🔴)

**D) "✅ Address created successfully"** → All working! ✅

---

## Database Connection Issues

If you see "Database connection failed":

```powershell
# Test MySQL directly
mysql -h localhost -u root -p123456 shopscaledb -e "SELECT 1;"

# If fails, check .env file has:
# DB_HOST=localhost
# DB_USER=root
# DB_PASSWORD=123456
# DB_NAME=shopscaledb
# DB_PORT=3306

# Or start MySQL
net start MySQL80
```

---

## Port Already in Use

If `python app.py` shows "Address already in use":

```powershell
# Kill Python process on port 5000
netstat -ano | findstr "5000"
# Note the PID (process ID) from output
taskkill /PID <PID> /F

# Then try again
python app.py
```

---

## Complete Working Flow

1. **Start Services**
   ```powershell
   net start MySQL80
   # Wait a moment for MySQL to start
   ```

2. **Start Backend** (new terminal)
   ```powershell
   cd C:\Users\gsche\OneDrive\Documents\db\backend
   python app.py
   # Should show: "Running on http://127.0.0.1:5000"
   ```

3. **Open Frontend**
   ```
   http://localhost:3000 (or your frontend port)
   ```

4. **Test Address Feature**
   - Login: rajesh.kumar@email.com / password123
   - Click "Addresses"
   - Click "Add New Address"
   - Fill: Street="123 Main St", City="Delhi", State="Delhi", Code="110001"
   - Click "Save"
   - Expected: "✅ Address added successfully!"

5. **Check Success**
   - Browser console: See ✅ messages
   - Address list: New address appears
   - Backend console: See 📦 and ✅ logs

---

## Emergency Reset

If everything is broken:

```powershell
# 1. Kill all Python processes
taskkill /F /IM python.exe

# 2. Restart MySQL
net stop MySQL80
net start MySQL80

# 3. Clear browser cache
# Ctrl + Shift + Delete in browser

# 4. Start fresh
cd C:\Users\gsche\OneDrive\Documents\db\backend
python app.py

# 5. Test
curl http://localhost:5000/api/health
```

---

## Still Stuck?

1. **Check console** (F12) for exact error message
2. **Screenshot** the error message
3. **Check backend** terminal for error logs (marked with 🔴)
4. **Run diagnostics**:
   ```powershell
   netstat -ano | findstr "5000"  # Backend
   netstat -ano | findstr "3306"  # MySQL
   tasklist | findstr "python"     # Python processes
   ```
5. **Open debug guide**: See `FETCH_ERROR_SOLUTIONS.md` for detailed help

---

## Success = All These True

✅ Backend running (http://localhost:5000/api/health returns JSON)
✅ MySQL running (port 3306 listening)
✅ Logged in (localStorage has token)
✅ Console shows ✅ messages not 🔴
✅ Address saves and appears in list
✅ No "Failed to fetch" errors

You're good to go! 🚀
