# 🚀 Production Quick Start

## Step 1: Get MongoDB Connection String

### Option A: MongoDB Atlas (Free Cloud Database)
1. Go to https://www.mongodb.com/cloud/atlas
2. Sign up / Log in
3. Create a free cluster (M0 Sandbox)
4. Create database user with `readWrite` permission
5. Whitelist your server's IP (or `0.0.0.0/0` for testing)
6. Get connection string from "Connect → Connect your application"
7. Replace `<password>` with your actual password

Example:
```
mongodb+srv://myuser:mypassword@cluster0.abc123.mongodb.net/?retryWrites=true&w=majority
```

### Option B: Local MongoDB
```
mongodb://localhost:27017/
```

---

## Step 2: Set MongoDB URI in Production

Choose ONE method:

### Method 1: Environment Variable (Most Secure) ⭐
```bash
export MONGODB_URI="mongodb+srv://user:pass@cluster.mongodb.net/"
export USE_MONGODB=true
python3 backend/server.py
```

### Method 2: .env File (Private Servers)
```bash
cd backend
cp .env.example .env
nano .env  # Add your MongoDB URI
python3 server.py
```

### Method 3: Platform-Specific

**Heroku:**
```bash
heroku config:set MONGODB_URI="mongodb+srv://..."
```

**Docker:**
```bash
docker run -e MONGODB_URI="mongodb+srv://..." your-image
```

**AWS/Linux:**
Add to `/etc/environment` or systemd service file

---

## Step 3: Deploy

```bash
python3 backend/server.py
```

---

## Verify It Works

```bash
cd backend
python3 test_mongodb.py
```

Should see:
```
✓ Connection successful
✓ Found X documents
✅ All tests passed!
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Connection timeout | Check MongoDB Atlas IP whitelist |
| Authentication failed | Verify username/password in URI |
| No module 'load_env' | Use environment variables instead |
| .env not loading | File must be in `backend/` directory |

---

## Important Security Notes

✅ **Never commit `.env` to Git** (already in `.gitignore`)
✅ **Use strong passwords** for MongoDB users
✅ **Restrict IP access** in MongoDB Atlas to your server only
✅ **Use environment variables** on cloud platforms (not .env files)

---

## Full Documentation

- **Complete Setup:** See `PRODUCTION_GUIDE.md`
- **MongoDB Features:** See `MONGODB_GUIDE.md`
- **Quick Reference:** See `MONGODB_INTEGRATION.md`

---

## Need Help?

1. Check logs: `python3 backend/server.py` (see errors)
2. Test connection: `python3 backend/test_mongodb.py`
3. Review docs: `PRODUCTION_GUIDE.md`
