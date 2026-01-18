# Deployment Guide 🚀

Complete guide for deploying Smart Document Extractor to production.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Prerequisites](#prerequisites)
3. [Configuration](#configuration)
4. [Deployment Methods](#deployment-methods)
5. [Production Checklist](#production-checklist)
6. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Automated Deployment

**Windows (PowerShell):**
```powershell
.\deploy.ps1
```

**Linux/Mac:**
```bash
chmod +x deploy.sh
./deploy.sh
```

**Or use Python directly:**
```bash
python deploy.py
```

---

## Prerequisites

### System Requirements

- **Python**: 3.8 or higher
- **RAM**: Minimum 4GB (8GB+ recommended for OCR models)
- **Disk Space**: 5GB+ (for OCR models and dependencies)
- **OS**: Windows, Linux, or macOS

### Required Software

1. **Python 3.8+**
2. **pip** (Python package manager)
3. **Virtual environment** (recommended)
4. **Database** (SQLite for testing, PostgreSQL/MySQL for production)

### Optional (for enhanced OCR)

- **Tesseract OCR**: System installation
  - Windows: Download from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
  - Linux: `sudo apt-get install tesseract-ocr`
  - Mac: `brew install tesseract`

---

## Configuration

### 1. Environment Variables

Copy the template and edit:
```bash
cp .env.example .env
```

Edit [.env](.env) file with your settings:

```env
# REQUIRED: Generate with: python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=your-generated-secret-key-here

# Database (choose one)
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname  # Production
# DATABASE_URL=mysql+pymysql://user:pass@localhost:3306/dbname
# DATABASE_URL=sqlite:///smart_doc_extractor.db  # Development only

# Optional: Translation API
GROQ_API_KEY=your-groq-api-key

# Optional: Custom Tesseract path
TESSERACT_CMD=/usr/bin/tesseract
```

### 2. Generate Secret Key

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output and set it as `SECRET_KEY` in your `.env` file.

### 3. Database Setup

**PostgreSQL (Recommended):**
```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Create database
sudo -u postgres createdb document_extractor
sudo -u postgres createuser dbuser
sudo -u postgres psql
postgres=# ALTER USER dbuser WITH PASSWORD 'your-password';
postgres=# GRANT ALL PRIVILEGES ON DATABASE document_extractor TO dbuser;
```

**MySQL:**
```bash
# Install MySQL
sudo apt-get install mysql-server

# Create database
mysql -u root -p
mysql> CREATE DATABASE document_extractor;
mysql> CREATE USER 'dbuser'@'localhost' IDENTIFIED BY 'your-password';
mysql> GRANT ALL PRIVILEGES ON document_extractor.* TO 'dbuser'@'localhost';
```

---

## Deployment Methods

### Method 1: Gunicorn (Linux/Mac) ⭐ Recommended

**1. Install dependencies:**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.production.txt
```

**2. Run with Gunicorn:**
```bash
gunicorn --bind 0.0.0.0:8000 \
         --workers 4 \
         --timeout 120 \
         --worker-class gevent \
         --log-level info \
         --access-logfile logs/access.log \
         --error-logfile logs/error.log \
         wsgi:app
```

**3. Create systemd service** ([document-extractor.service](document-extractor.service)):
```ini
[Unit]
Description=Smart Document Extractor
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/app
Environment="PATH=/path/to/app/venv/bin"
ExecStart=/path/to/app/venv/bin/gunicorn \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --timeout 120 \
    wsgi:app

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo cp document-extractor.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable document-extractor
sudo systemctl start document-extractor
sudo systemctl status document-extractor
```

---

### Method 2: Waitress (Windows) ⭐ Recommended for Windows

**1. Install dependencies:**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.production.txt
```

**2. Run with Waitress:**
```powershell
waitress-serve --host=0.0.0.0 --port=8000 --threads=4 wsgi:app
```

**3. Create Windows Service** (using NSSM):
```powershell
# Download NSSM from https://nssm.cc/download
nssm install DocumentExtractor "C:\path\to\venv\Scripts\waitress-serve.exe"
nssm set DocumentExtractor AppParameters "--host=0.0.0.0 --port=8000 wsgi:app"
nssm set DocumentExtractor AppDirectory "C:\path\to\app"
nssm start DocumentExtractor
```

---

### Method 3: Docker 🐳

**1. Build image:**
```bash
docker build -t document-extractor .
```

**2. Run container:**
```bash
docker run -d \
  -p 8000:8000 \
  --env-file .env \
  -v $(pwd)/static/uploads:/app/static/uploads \
  --name document-extractor \
  document-extractor
```

**3. Using Docker Compose:**
```bash
docker-compose up -d
```

---

### Method 4: Cloud Platforms

#### Heroku

```bash
# Install Heroku CLI
# Login
heroku login

# Create app
heroku create your-app-name

# Add PostgreSQL
heroku addons:create heroku-postgresql:mini

# Set environment variables
heroku config:set SECRET_KEY=your-secret-key
heroku config:set FLASK_ENV=production

# Deploy
git push heroku main

# Run migrations
heroku run python -c "from app import create_app; from models import db; app = create_app(); app.app_context().push(); db.create_all()"
```

#### AWS Elastic Beanstalk

```bash
# Install EB CLI
pip install awsebcli

# Initialize
eb init -p python-3.11 document-extractor

# Create environment
eb create production-env

# Deploy
eb deploy

# Set environment variables
eb setenv SECRET_KEY=your-secret-key FLASK_ENV=production
```

#### Google Cloud Platform (App Engine)

Create [app.yaml](app.yaml):
```yaml
runtime: python311

entrypoint: gunicorn -b :$PORT wsgi:app

env_variables:
  SECRET_KEY: "your-secret-key"
  FLASK_ENV: "production"
```

Deploy:
```bash
gcloud app deploy
```

---

## Reverse Proxy Setup

### Nginx Configuration

Create `/etc/nginx/sites-available/document-extractor`:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # File upload size
    client_max_body_size 16M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
    }

    location /static {
        alias /path/to/app/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

Enable and restart:
```bash
sudo ln -s /etc/nginx/sites-available/document-extractor /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Apache Configuration

```apache
<VirtualHost *:80>
    ServerName yourdomain.com
    Redirect permanent / https://yourdomain.com/
</VirtualHost>

<VirtualHost *:443>
    ServerName yourdomain.com

    SSLEngine on
    SSLCertificateFile /etc/letsencrypt/live/yourdomain.com/fullchain.pem
    SSLCertificateKeyFile /etc/letsencrypt/live/yourdomain.com/privkey.pem

    ProxyPreserveHost On
    ProxyPass / http://127.0.0.1:8000/
    ProxyPassReverse / http://127.0.0.1:8000/
    
    ProxyTimeout 120
</VirtualHost>
```

---

## SSL Certificate (Let's Encrypt)

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal (should be automatic)
sudo certbot renew --dry-run
```

---

## Production Checklist

### Security ✅

- [ ] Set strong `SECRET_KEY` (64+ random characters)
- [ ] Use PostgreSQL or MySQL (not SQLite)
- [ ] Enable HTTPS/SSL
- [ ] Configure firewall (allow only 80, 443)
- [ ] Set up rate limiting
- [ ] Enable CSRF protection
- [ ] Configure secure session cookies
- [ ] Remove debug mode (`DEBUG=False`)
- [ ] Set proper file permissions (chmod 600 for .env)
- [ ] Regular security updates

### Performance ✅

- [ ] Use production WSGI server (Gunicorn/Waitress)
- [ ] Configure multiple workers (4-8 recommended)
- [ ] Set up reverse proxy (Nginx/Apache)
- [ ] Enable static file caching
- [ ] Configure upload size limits
- [ ] Monitor memory usage
- [ ] Set up CDN (optional, for static files)

### Monitoring ✅

- [ ] Set up application logging
- [ ] Configure error tracking (Sentry)
- [ ] Monitor server resources (CPU, RAM, disk)
- [ ] Set up uptime monitoring
- [ ] Configure backup alerts
- [ ] Application metrics dashboard

### Backup ✅

- [ ] Database automated backups
- [ ] Upload files backup
- [ ] Configuration backup (.env)
- [ ] Test restore procedures
- [ ] Off-site backup storage

### Maintenance ✅

- [ ] Documentation for team
- [ ] Deployment runbook
- [ ] Rollback procedures
- [ ] Update procedures
- [ ] Contact information

---

## Monitoring & Logging

### Application Logging

The application logs to:
- `logs/access.log` - HTTP requests
- `logs/error.log` - Application errors

### System Monitoring

**Using systemd:**
```bash
# Check status
sudo systemctl status document-extractor

# View logs
sudo journalctl -u document-extractor -f

# Restart service
sudo systemctl restart document-extractor
```

### Error Tracking with Sentry

1. Sign up at [sentry.io](https://sentry.io)
2. Get your DSN
3. Add to [.env](.env):
   ```env
   SENTRY_DSN=your-sentry-dsn
   ```

---

## Troubleshooting

### Application won't start

**Check logs:**
```bash
# Systemd
sudo journalctl -u document-extractor -n 50

# Direct run
gunicorn --log-level debug wsgi:app
```

**Common issues:**
- Missing SECRET_KEY in .env
- Database connection failed
- Port already in use
- Permission denied for uploads folder

### Database connection errors

```bash
# Test database connection
python -c "from app import create_app; app = create_app(); print('Database OK')"

# Check PostgreSQL
sudo systemctl status postgresql
psql -U dbuser -d document_extractor
```

### OCR models not downloading

```bash
# Check internet connection
ping huggingface.co

# Manual download location
ls ~/.cache/huggingface/

# Set custom cache directory
export HF_HOME=/path/to/cache
```

### High memory usage

- Reduce number of workers
- Use worker class: `--worker-class gevent`
- Increase system swap
- Consider upgrading server RAM

### File upload errors

```bash
# Check upload directory permissions
ls -la static/uploads/

# Fix permissions
sudo chown -R www-data:www-data static/uploads/
sudo chmod -R 755 static/uploads/
```

---

## Performance Optimization

### Worker Configuration

**CPU-bound tasks (OCR):**
```bash
workers = (2 x CPU_cores) + 1
# Example: 4 cores = 9 workers
```

**Memory considerations:**
```bash
# Each worker uses ~500MB-1GB with OCR models loaded
# For 8GB RAM: 4-6 workers recommended
```

### Database Optimization

**PostgreSQL:**
```sql
-- Add indexes
CREATE INDEX idx_documents_user ON documents(user_id);
CREATE INDEX idx_documents_created ON documents(created_at);

-- Analyze tables
ANALYZE documents;
```

### Caching

Consider adding Redis for:
- Session storage
- OCR result caching
- Rate limiting

---

## Scaling

### Horizontal Scaling

1. **Load Balancer**: Nginx/HAProxy
2. **Multiple App Servers**: Run on different machines
3. **Shared Storage**: NFS/S3 for uploads
4. **Centralized Database**: PostgreSQL cluster
5. **Session Store**: Redis cluster

### Vertical Scaling

- Increase CPU cores
- Add more RAM
- Faster SSD storage
- GPU for OCR processing

---

## Security Best Practices

1. **Keep dependencies updated:**
   ```bash
   pip list --outdated
   pip install --upgrade package-name
   ```

2. **Regular security audits:**
   ```bash
   pip install safety
   safety check
   ```

3. **Environment isolation:**
   - Use virtual environments
   - Separate development/production
   - Different databases for each environment

4. **Access control:**
   - Strong passwords
   - Two-factor authentication
   - Role-based access control
   - Regular permission audits

---

## Support

For issues and questions:
- Check application logs
- Review this documentation
- Search existing issues
- Create new issue with:
  - Error messages
  - Environment details
  - Steps to reproduce

---

## Additional Resources

- [Flask Deployment Options](https://flask.palletsprojects.com/en/2.3.x/deploying/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Let's Encrypt](https://letsencrypt.org/)

---

**Last Updated:** January 2026
