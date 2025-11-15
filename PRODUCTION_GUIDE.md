# Production Deployment Guide

## Setting MongoDB URI in Production

### 🔒 Security First!

**NEVER commit your MongoDB connection string to Git!**

The `.env` file and any file containing credentials should be in `.gitignore`.

---

## Deployment Options

### Option 1: Environment Variables (Recommended)

Set environment variables directly on your production platform. This is the most secure method.

#### **Heroku**
```bash
heroku config:set MONGODB_URI="mongodb+srv://user:pass@cluster.mongodb.net/"
heroku config:set USE_MONGODB=true
```

#### **AWS EC2 / Linux Server**
Add to `/etc/environment` or systemd service file:
```bash
export MONGODB_URI="mongodb+srv://user:pass@cluster.mongodb.net/"
export USE_MONGODB=true
export PORT=5000
```

Then in your startup script:
```bash
source /etc/environment
python3 server.py
```

#### **Docker**
```bash
docker run -p 5000:5000 \
  -e MONGODB_URI="mongodb+srv://..." \
  -e USE_MONGODB=true \
  your-search-engine
```

Or with docker-compose.yml:
```yaml
version: '3.8'
services:
  search-engine:
    image: your-search-engine
    ports:
      - "5000:5000"
    environment:
      MONGODB_URI: "${MONGODB_URI}"
      USE_MONGODB: "true"
      PORT: "5000"
```

Then create `.env` file (not committed):
```bash
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/
```

Run with:
```bash
docker-compose up
```

#### **Kubernetes**
Create a Secret:
```bash
kubectl create secret generic search-engine-secrets \
  --from-literal=mongodb-uri='mongodb+srv://user:pass@cluster.mongodb.net/'
```

Reference in deployment.yaml:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: search-engine
spec:
  template:
    spec:
      containers:
      - name: search-engine
        image: your-search-engine
        env:
        - name: MONGODB_URI
          valueFrom:
            secretKeyRef:
              name: search-engine-secrets
              key: mongodb-uri
        - name: USE_MONGODB
          value: "true"
```

#### **Azure App Service**
```bash
az webapp config appsettings set \
  --name your-app-name \
  --resource-group your-resource-group \
  --settings MONGODB_URI="mongodb+srv://..." USE_MONGODB=true
```

#### **Google Cloud Run**
```bash
gcloud run deploy search-engine \
  --set-env-vars MONGODB_URI="mongodb+srv://...",USE_MONGODB=true
```

---

### Option 2: .env File (Private Servers)

For your own private servers where you control access:

1. **Copy the example:**
   ```bash
   cd backend
   cp .env.example .env
   ```

2. **Edit `.env` with your credentials:**
   ```bash
   MONGODB_URI=mongodb+srv://your-user:your-password@cluster.mongodb.net/
   USE_MONGODB=true
   PORT=5000
   ```

3. **Secure the file:**
   ```bash
   chmod 600 .env
   ```

4. **Start the server:**
   ```bash
   python3 server.py
   ```

The server automatically loads `.env` on startup!

---

### Option 3: Secrets Management (Enterprise)

#### **AWS Secrets Manager**
```python
import boto3
import json

def get_mongodb_uri():
    client = boto3.client('secretsmanager', region_name='us-east-1')
    response = client.get_secret_value(SecretId='prod/search-engine/mongodb')
    secret = json.loads(response['SecretString'])
    return secret['MONGODB_URI']
```

#### **HashiCorp Vault**
```bash
vault kv get -field=mongodb_uri secret/search-engine
```

#### **Azure Key Vault**
```bash
az keyvault secret show \
  --name mongodb-uri \
  --vault-name your-vault \
  --query value -o tsv
```

---

## MongoDB Atlas Setup (Recommended)

MongoDB Atlas is the easiest way to get a production MongoDB:

1. **Sign up:** https://www.mongodb.com/cloud/atlas

2. **Create a free cluster** (M0 Sandbox)

3. **Create a database user:**
   - Database Access → Add New Database User
   - Username: `search_engine_user`
   - Password: Generate secure password
   - Built-in Role: `readWrite` on `crawler_db`

4. **Whitelist your IP:**
   - Network Access → Add IP Address
   - For development: Add Current IP
   - For production: Add your server's IP or `0.0.0.0/0` (less secure)

5. **Get connection string:**
   - Connect → Connect your application
   - Choose Python driver
   - Copy the connection string:
   ```
   mongodb+srv://search_engine_user:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
   - Replace `<password>` with your actual password

6. **Set it in production:**
   ```bash
   export MONGODB_URI="mongodb+srv://search_engine_user:your-password@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority"
   ```

---

## Security Checklist

- [ ] MongoDB URI contains credentials? Use environment variables or secrets management
- [ ] `.env` file in `.gitignore`?
- [ ] Production MongoDB has authentication enabled?
- [ ] MongoDB network access restricted to your server's IP?
- [ ] Using strong passwords for MongoDB users?
- [ ] TLS/SSL enabled for MongoDB connections?
- [ ] Environment variables not printed in logs?

---

## Verification

Test your production setup:

```bash
cd backend
python3 test_mongodb.py
```

Should output:
```
✓ Connection successful
✓ Found X documents in crawled_pages collection
✓ MongoSearchEngine initialized
✅ All tests passed!
```

---

## Example: Complete Production Setup

### Using Nginx + Systemd (Linux Server)

1. **Create `.env` file:**
   ```bash
   sudo nano /opt/search-engine/backend/.env
   ```

   Add:
   ```
   MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/
   USE_MONGODB=true
   PORT=5000
   ```

2. **Create systemd service:**
   ```bash
   sudo nano /etc/systemd/system/search-engine.service
   ```

   Add:
   ```ini
   [Unit]
   Description=Search Engine API
   After=network.target

   [Service]
   Type=simple
   User=www-data
   WorkingDirectory=/opt/search-engine/backend
   ExecStart=/usr/bin/python3 /opt/search-engine/backend/server.py
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

3. **Start service:**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable search-engine
   sudo systemctl start search-engine
   ```

4. **Check status:**
   ```bash
   sudo systemctl status search-engine
   ```

5. **Configure Nginx:**
   ```nginx
   server {
       listen 80;
       server_name yourdomain.com;

       location /api/ {
           proxy_pass http://localhost:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }

       location /ws/ {
           proxy_pass http://localhost:5000;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
       }

       location / {
           root /opt/search-engine/frontend/build;
           try_files $uri /index.html;
       }
   }
   ```

---

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `MONGODB_URI` | Yes* | `mongodb://localhost:27017/` | MongoDB connection string |
| `USE_MONGODB` | No | `true` | Enable MongoDB (set to `false` for file-based) |
| `PORT` | No | `5000` | Server port |
| `DATA_DIR` | No | `./data` | Fallback data directory |

*Required if `USE_MONGODB=true`

---

## Troubleshooting

### "Authentication failed"
- Check your username and password in the connection string
- Verify the database user has `readWrite` permissions

### "Connection timeout"
- Check MongoDB Atlas network access settings
- Verify your server's IP is whitelisted
- Check firewall rules

### "No module named 'load_env'"
- Make sure `load_env.py` is in the backend directory
- Or just use environment variables directly

### ".env file not loading"
- File must be named exactly `.env` (not `.env.txt`)
- Must be in the `backend/` directory
- Check file permissions: `chmod 600 .env`

---

## Best Practices

1. **Use MongoDB Atlas** for production (managed, secure, backed up)
2. **Set environment variables** at the platform level (not in code)
3. **Use secrets management** for enterprise deployments
4. **Enable SSL/TLS** for MongoDB connections
5. **Restrict network access** to your server's IP only
6. **Use strong passwords** (20+ characters, random)
7. **Create separate MongoDB users** for dev/staging/prod
8. **Monitor your database** (Atlas provides free monitoring)
9. **Set up backups** (Atlas does this automatically)
10. **Rotate credentials** periodically

---

## Quick Reference

**Development (local MongoDB):**
```bash
export MONGODB_URI="mongodb://localhost:27017/"
./start.sh
```

**Production (MongoDB Atlas):**
```bash
export MONGODB_URI="mongodb+srv://user:pass@cluster.mongodb.net/"
python3 backend/server.py
```

**Docker Production:**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY backend/ /app/
RUN pip install -r requirements.txt
ENV USE_MONGODB=true
CMD ["python", "server.py"]
```

Build and run:
```bash
docker build -t search-engine .
docker run -p 5000:5000 -e MONGODB_URI="mongodb+srv://..." search-engine
```

---

Need help? Check the logs:
```bash
# Systemd service logs
sudo journalctl -u search-engine -f

# Docker logs
docker logs -f container-name

# Direct Python logs
python3 server.py
```
