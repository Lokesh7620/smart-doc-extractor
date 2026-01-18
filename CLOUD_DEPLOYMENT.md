# Cloud Deployment Guide - Public Access

This guide covers deploying your Smart Document Extractor to the cloud for permanent public access.

## Table of Contents
- [Quick Public Access (ngrok)](#quick-public-access-ngrok)
- [Cloud Deployment Options](#cloud-deployment-options)
- [Option 1: Render.com (Easiest)](#option-1-rendercom-easiest)
- [Option 2: Railway.app](#option-2-railwayapp)
- [Option 3: DigitalOcean App Platform](#option-3-digitalocean-app-platform)
- [Option 4: AWS EC2](#option-4-aws-ec2)
- [Option 5: Heroku](#option-5-heroku)

---

## Quick Public Access (ngrok)

**Best for:** Testing, demos, temporary sharing
**Cost:** Free (with limitations)
**Setup time:** 5 minutes

### Steps:

1. **Install ngrok:**
   - Download from: https://ngrok.com/download
   - Extract and add to PATH or move to `C:\Windows\System32\`

2. **Get auth token:**
   - Sign up at: https://dashboard.ngrok.com/signup
   - Copy your auth token
   - Run: `ngrok config add-authtoken YOUR_AUTH_TOKEN`

3. **Deploy:**
   ```powershell
   python public_deploy_ngrok.py
   ```

4. **Access:**
   - You'll get a public URL like: `https://abc123.ngrok.io`
   - Share this URL with anyone
   - View traffic at: http://127.0.0.1:4040

**Limitations:**
- URL changes on restart (use paid plan for static URLs)
- 40 requests/minute on free plan
- Sessions timeout after 2 hours

---

## Cloud Deployment Options

### Comparison Table

| Platform | Difficulty | Cost/Month | Free Tier | Build Time | SSL | Domain |
|----------|-----------|------------|-----------|------------|-----|--------|
| **Render** | ⭐ Easy | $7+ | Yes (750hrs) | ~10 min | ✅ Free | ✅ Custom |
| **Railway** | ⭐ Easy | $5+ | $5 credit | ~5 min | ✅ Free | ✅ Custom |
| **DigitalOcean** | ⭐⭐ Medium | $4+ | $200 credit | ~15 min | ✅ Free | ✅ Custom |
| **AWS EC2** | ⭐⭐⭐ Hard | $5+ | 12mo free | ~30 min | ⚠️ Setup | ⚠️ Setup |
| **Heroku** | ⭐ Easy | $5+ | No | ~10 min | ✅ Free | ✅ Custom |

---

## Option 1: Render.com (Easiest)

**Recommended for beginners - Free tier available**

### Prerequisites:
- GitHub account
- Credit card (for verification, not charged on free tier)

### Steps:

1. **Push code to GitHub:**
   ```powershell
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/smart-doc-extractor.git
   git push -u origin main
   ```

2. **Create Render account:**
   - Go to: https://render.com
   - Sign up with GitHub

3. **Create PostgreSQL database:**
   - Click "New +" → "PostgreSQL"
   - Name: `document-extractor-db`
   - Plan: Free
   - Click "Create Database"
   - **Copy the Internal Database URL** (starts with `postgresql://`)

4. **Create Web Service:**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Configuration:
     - **Name:** `smart-doc-extractor`
     - **Environment:** Python 3
     - **Build Command:** `pip install -r requirements.production.txt`
     - **Start Command:** `gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 wsgi:app`

5. **Add Environment Variables:**
   ```
   SECRET_KEY=<generate new 64-char hex>
   DATABASE_URL=<paste from step 3>
   GROQ_API_KEY=your_groq_api_key_here
   FLASK_ENV=production
   FLASK_CONFIG=config_production.ProductionConfig
   PYTHON_VERSION=3.11
   ```

6. **Deploy:**
   - Click "Create Web Service"
   - Wait ~10 minutes for build
   - Your app will be at: `https://smart-doc-extractor.onrender.com`

7. **Add Custom Domain (Optional):**
   - Settings → Custom Domains → Add Custom Domain
   - Point your domain's DNS to Render

**Free Tier Limits:**
- 750 hours/month
- 512MB RAM
- Sleeps after 15min inactivity (wakes in ~30s)

---

## Option 2: Railway.app

**Fast deployment with great DX**

### Steps:

1. **Push to GitHub** (same as Render step 1)

2. **Create Railway account:**
   - Go to: https://railway.app
   - Sign in with GitHub
   - Get $5 free credit

3. **New Project:**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

4. **Add PostgreSQL:**
   - Click "+ New"
   - Select "Database" → "PostgreSQL"
   - Railway auto-configures DATABASE_URL

5. **Configure Service:**
   - Click your web service
   - Variables tab → Add:
     ```
     SECRET_KEY=<64-char hex>
     GROQ_API_KEY=your_groq_api_key_here
     FLASK_ENV=production
     FLASK_CONFIG=config_production.ProductionConfig
     PORT=8000
     ```

6. **Settings:**
   - Build Command: `pip install -r requirements.production.txt`
   - Start Command: `gunicorn --bind 0.0.0.0:$PORT --workers 2 wsgi:app`

7. **Deploy:**
   - Railway auto-deploys
   - Get public URL from "Deployments" tab
   - Add custom domain in Settings → Domains

**Pricing:**
- $5/month after free credit
- Pay-as-you-go

---

## Option 3: DigitalOcean App Platform

**Great for scaling**

### Steps:

1. **Create DO account:**
   - Go to: https://www.digitalocean.com
   - Get $200 credit (60 days)

2. **Create App:**
   - Apps → "Create App"
   - Choose GitHub
   - Select repository and branch

3. **Configure:**
   - **Name:** smart-doc-extractor
   - **Plan:** Basic ($4/mo)
   - **Build Command:** `pip install -r requirements.production.txt`
   - **Run Command:** `gunicorn --bind 0.0.0.0:$PORT --workers 2 wsgi:app`

4. **Add Database:**
   - Create → Databases → PostgreSQL
   - Plan: $15/mo (or use external like Supabase)
   - Get DATABASE_URL from connection details

5. **Environment Variables:**
   ```
   SECRET_KEY=<64-char hex>
   DATABASE_URL=<from database>
   GROQ_API_KEY=your_groq_api_key_here
   FLASK_ENV=production
   FLASK_CONFIG=config_production.ProductionConfig
   ```

6. **Deploy:**
   - Click "Create Resources"
   - Wait 10-15 minutes
   - Access at provided URL

**Pricing:**
- App: $4-12/month
- Database: $15/month
- $200 free credit for new accounts

---

## Option 4: AWS EC2

**Full control, more complex**

### Steps:

1. **Launch EC2 Instance:**
   - Go to AWS Console → EC2
   - Launch Instance
   - **AMI:** Ubuntu 22.04 LTS
   - **Type:** t2.micro (free tier) or t2.small
   - **Security Group:** Allow ports 22, 80, 443

2. **Connect via SSH:**
   ```bash
   ssh -i your-key.pem ubuntu@YOUR_IP
   ```

3. **Install dependencies:**
   ```bash
   sudo apt update
   sudo apt install -y python3-pip python3-venv nginx postgresql tesseract-ocr
   ```

4. **Clone repository:**
   ```bash
   cd /var/www
   sudo git clone https://github.com/YOUR_USERNAME/smart-doc-extractor.git
   cd smart-doc-extractor
   ```

5. **Setup application:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.production.txt
   
   # Create .env
   sudo nano .env
   # Add: SECRET_KEY, DATABASE_URL, etc.
   ```

6. **Configure PostgreSQL:**
   ```bash
   sudo -u postgres psql
   CREATE DATABASE document_extractor;
   CREATE USER dbuser WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE document_extractor TO dbuser;
   \q
   ```

7. **Setup Gunicorn service:**
   ```bash
   sudo cp document-extractor.service /etc/systemd/system/
   sudo systemctl enable document-extractor
   sudo systemctl start document-extractor
   ```

8. **Configure Nginx:**
   ```bash
   sudo cp nginx.conf /etc/nginx/sites-available/document-extractor
   sudo ln -s /etc/nginx/sites-available/document-extractor /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

9. **Get SSL Certificate:**
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d yourdomain.com
   ```

**Pricing:**
- t2.micro: Free tier (12 months)
- t2.small: ~$17/month
- Elastic IP: Free if attached

---

## Option 5: Heroku

**Classic PaaS**

### Steps:

1. **Install Heroku CLI:**
   ```powershell
   winget install Heroku.HerokuCLI
   ```

2. **Login:**
   ```powershell
   heroku login
   ```

3. **Create app:**
   ```powershell
   cd "D:\1 Deploy"
   heroku create smart-doc-extractor
   ```

4. **Add PostgreSQL:**
   ```powershell
   heroku addons:create heroku-postgresql:mini
   ```

5. **Set environment variables:**
   ```powershell
   heroku config:set SECRET_KEY=<64-char-hex>
   heroku config:set GROQ_API_KEY=your_groq_api_key_here
   heroku config:set FLASK_ENV=production
   heroku config:set FLASK_CONFIG=config_production.ProductionConfig
   ```

6. **Create Procfile:**
   ```
   web: gunicorn --bind 0.0.0.0:$PORT --workers 2 wsgi:app
   ```

7. **Deploy:**
   ```powershell
   git init
   git add .
   git commit -m "Deploy to Heroku"
   heroku git:remote -a smart-doc-extractor
   git push heroku main
   ```

8. **Open:**
   ```powershell
   heroku open
   ```

**Pricing:**
- Eco dyno: $5/month
- Mini Postgres: $5/month
- Total: $10/month

---

## Post-Deployment Checklist

After deploying to any platform:

- ✅ Test registration/login
- ✅ Test document upload
- ✅ Test OCR extraction
- ✅ Test translation
- ✅ Verify SSL certificate (https://)
- ✅ Test on mobile devices
- ✅ Set up monitoring (Sentry, UptimeRobot)
- ✅ Configure backups (database dumps)
- ✅ Set up custom domain
- ✅ Add to Google Search Console
- ✅ Test performance (GTmetrix)

---

## Recommended: Render.com

**For this project, I recommend Render.com because:**
1. ✅ Free tier available (750hrs/month)
2. ✅ Easiest setup (5-minute deployment)
3. ✅ Auto-SSL certificates
4. ✅ Auto-scaling
5. ✅ GitHub integration with auto-deploys
6. ✅ Free PostgreSQL on free tier
7. ✅ Great for Python/Flask apps

**Quick Deploy to Render:**
```powershell
# Run this script for automated Render deployment
python deploy_to_render.py
```

---

## Support

For issues or questions:
- Check DEPLOYMENT.md for general troubleshooting
- Platform-specific docs:
  - Render: https://render.com/docs
  - Railway: https://docs.railway.app
  - DigitalOcean: https://docs.digitalocean.com
  - AWS: https://docs.aws.amazon.com

---

## Security Notes

**Before going public:**
1. ✅ Change SECRET_KEY to new random value
2. ✅ Use strong database passwords
3. ✅ Enable HTTPS only
4. ✅ Set up rate limiting
5. ✅ Configure CORS if needed
6. ✅ Review ProductionConfig settings
7. ✅ Set up monitoring/alerting
8. ✅ Regular backups
9. ✅ Keep dependencies updated
10. ✅ Add Sentry for error tracking
