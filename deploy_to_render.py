#!/usr/bin/env python3
"""
Automated Render.com Deployment Script
Prepares the project for deployment to Render.com
"""
import os
import secrets
import json
from pathlib import Path

def generate_secret_key():
    """Generate a secure SECRET_KEY"""
    return secrets.token_hex(32)

def create_render_yaml():
    """Create render.yaml for automated deployment"""
    
    secret_key = generate_secret_key()
    
    render_config = {
        "services": [
            {
                "type": "web",
                "name": "smart-doc-extractor",
                "env": "python",
                "plan": "free",
                "buildCommand": "pip install -r requirements.production.txt",
                "startCommand": "gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 wsgi:app",
                "healthCheckPath": "/",
                "envVars": [
                    {
                        "key": "PYTHON_VERSION",
                        "value": "3.11"
                    },
                    {
                        "key": "FLASK_ENV",
                        "value": "production"
                    },
                    {
                        "key": "FLASK_CONFIG",
                        "value": "config_production.ProductionConfig"
                    },
                    {
                        "key": "SECRET_KEY",
                        "generateValue": True
                    },
                    {
                        "key": "DATABASE_URL",
                        "fromDatabase": {
                            "name": "document-extractor-db",
                            "property": "connectionString"
                        }
                    },
                    {
                        "key": "GROQ_API_KEY",
                        "value": "your_groq_api_key_here"
                    }
                ]
            }
        ],
        "databases": [
            {
                "name": "document-extractor-db",
                "plan": "free",
                "databaseName": "document_extractor",
                "user": "dbuser"
            }
        ]
    }
    
    # Save render.yaml
    yaml_path = Path(__file__).parent / 'render.yaml'
    
    # Convert to YAML format manually (avoid PyYAML dependency)
    yaml_content = """services:
  - type: web
    name: smart-doc-extractor
    env: python
    plan: free
    buildCommand: pip install -r requirements.production.txt
    startCommand: gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 wsgi:app
    healthCheckPath: /
    envVars:
      - key: PYTHON_VERSION
        value: "3.11"
      - key: FLASK_ENV
        value: production
      - key: FLASK_CONFIG
        value: config_production.ProductionConfig
      - key: SECRET_KEY
        generateValue: true
      - key: DATABASE_URL
        fromDatabase:
          name: document-extractor-db
          property: connectionString
      - key: GROQ_API_KEY
        value: your_groq_api_key_here

databases:
  - name: document-extractor-db
    plan: free
    databaseName: document_extractor
    user: dbuser
"""
    
    with open(yaml_path, 'w') as f:
        f.write(yaml_content)
    
    print(f"✅ Created render.yaml")
    return yaml_path

def create_runtime_txt():
    """Create runtime.txt for Python version"""
    runtime_path = Path(__file__).parent / 'runtime.txt'
    with open(runtime_path, 'w') as f:
        f.write('python-3.11.0\n')
    print(f"✅ Created runtime.txt")
    return runtime_path

def update_gitignore():
    """Update .gitignore to not ignore render.yaml"""
    gitignore_path = Path(__file__).parent / '.gitignore'
    
    if gitignore_path.exists():
        with open(gitignore_path, 'r') as f:
            content = f.read()
        
        # Make sure .env is ignored but not render.yaml
        if '.env' not in content:
            with open(gitignore_path, 'a') as f:
                f.write('\n# Environment files\n.env\n.env.local\n')
        
        print(f"✅ Updated .gitignore")
    else:
        with open(gitignore_path, 'w') as f:
            f.write('.env\n.env.local\n__pycache__/\n*.pyc\n')
        print(f"✅ Created .gitignore")

def create_deployment_instructions():
    """Create deployment instructions file"""
    instructions_path = Path(__file__).parent / 'RENDER_DEPLOY_STEPS.md'
    
    instructions = """# Deploy to Render.com - Step by Step

## 🚀 Automated Setup Complete!

Your project is now ready for Render.com deployment. Follow these steps:

## Option A: Deploy via GitHub (Recommended)

### 1. Push to GitHub

```powershell
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Ready for Render deployment"

# Create repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/smart-doc-extractor.git
git branch -M main
git push -u origin main
```

### 2. Connect to Render

1. Go to: https://render.com
2. Sign up / Log in with GitHub
3. Click **"New +"** → **"Blueprint"**
4. Select your repository
5. Render will auto-detect `render.yaml` and configure everything
6. Click **"Apply"**

### 3. Wait for Deployment

- Database creation: ~2 minutes
- App build: ~8-10 minutes
- Total: ~12 minutes

### 4. Access Your App

- You'll get a URL like: `https://smart-doc-extractor.onrender.com`
- Initial request may take 30 seconds (free tier sleeps after inactivity)

## Option B: Manual Deployment

If you prefer manual setup:

### 1. Create Render Account
- Go to https://render.com and sign up

### 2. Create PostgreSQL Database
- Click **"New +"** → **"PostgreSQL"**
- **Name:** `document-extractor-db`
- **Database:** `document_extractor`
- **User:** `dbuser`
- **Plan:** Free
- Click **"Create Database"**
- **Save the Internal Database URL** (you'll need it in step 4)

### 3. Create Web Service
- Click **"New +"** → **"Web Service"**
- Connect your GitHub repository OR upload code
- Configuration:
  - **Name:** `smart-doc-extractor`
  - **Environment:** Python 3
  - **Region:** Choose closest to you
  - **Branch:** main
  - **Build Command:** `pip install -r requirements.production.txt`
  - **Start Command:** `gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 wsgi:app`
  - **Plan:** Free

### 4. Add Environment Variables

In the **Environment** section, add:

```
PYTHON_VERSION=3.11
FLASK_ENV=production
FLASK_CONFIG=config_production.ProductionConfig
SECRET_KEY=<click "Generate" button for secure key>
DATABASE_URL=<paste Internal Database URL from step 2>
GROQ_API_KEY=your_groq_api_key_here
```

### 5. Deploy
- Click **"Create Web Service"**
- Wait 8-10 minutes for build

## ✅ Post-Deployment

### Test Your App

1. Open your Render URL
2. Register a new account
3. Upload a document
4. Test OCR extraction
5. Test translation

### Add Custom Domain (Optional)

1. Go to your web service settings
2. Click **"Custom Domains"**
3. Add your domain (e.g., `app.yourdomain.com`)
4. Update your DNS:
   - **Type:** CNAME
   - **Name:** app
   - **Value:** your-app.onrender.com

### Monitoring

- View logs: Service → Logs
- View metrics: Service → Metrics
- Set up alerts: Service → Settings → Notifications

## 🔧 Configuration Files Created

✅ `render.yaml` - Automated deployment config
✅ `runtime.txt` - Python version specification
✅ `.gitignore` - Git ignore rules
✅ `requirements.production.txt` - Production dependencies

## 💡 Tips

### Free Tier Limitations
- ⚠️ Sleeps after 15 minutes of inactivity
- ⚠️ Takes ~30 seconds to wake up
- ⚠️ 750 hours/month (unlimited if always on)
- ✅ Free SSL certificate
- ✅ Auto-deploys on git push

### Upgrade to Paid ($7/mo)
- ✅ No sleep
- ✅ Faster builds
- ✅ More resources

### Keep Free Tier Active
Use a service like UptimeRobot to ping your app every 5 minutes:
1. Sign up at: https://uptimerobot.com
2. Add monitor with your Render URL
3. Set interval to 5 minutes

## 🆘 Troubleshooting

### Build Failed
- Check logs in Render dashboard
- Verify requirements.production.txt includes all dependencies
- Check Python version matches runtime.txt

### App Won't Start
- Verify DATABASE_URL is set
- Check SECRET_KEY is generated
- Review startup logs

### Database Connection Error
- Ensure DATABASE_URL points to Internal Database URL
- Check database is running (Render → Databases)
- Verify database credentials

### OCR Not Working
- Free tier has limited memory (512MB)
- TrOCR and PaddleOCR are memory-intensive
- Upgrade to Starter plan for more RAM

## 📚 Additional Resources

- Render Docs: https://render.com/docs
- Python Guide: https://render.com/docs/deploy-flask
- Database Guide: https://render.com/docs/databases
- Custom Domains: https://render.com/docs/custom-domains

## 🎉 Next Steps

Once deployed:
1. ✅ Test all features
2. ✅ Add custom domain
3. ✅ Set up monitoring
4. ✅ Configure database backups
5. ✅ Add error tracking (Sentry)
6. ✅ Optimize performance

---

**Your app is ready to deploy! Choose Option A for the easiest deployment.**
"""
    
    with open(instructions_path, 'w', encoding='utf-8') as f:
        f.write(instructions)
    
    print(f"✅ Created RENDER_DEPLOY_STEPS.md")
    return instructions_path

def main():
    """Main deployment preparation function"""
    print("\n" + "="*70)
    print("RENDER.COM DEPLOYMENT PREPARATION")
    print("="*70)
    
    # Create necessary files
    create_render_yaml()
    create_runtime_txt()
    update_gitignore()
    instructions_file = create_deployment_instructions()
    
    print("\n" + "="*70)
    print("✅ DEPLOYMENT PREPARATION COMPLETE!")
    print("="*70)
    print("\nFiles created:")
    print("  ✅ render.yaml - Automated deployment config")
    print("  ✅ runtime.txt - Python version")
    print("  ✅ RENDER_DEPLOY_STEPS.md - Detailed instructions")
    
    print("\n" + "="*70)
    print("NEXT STEPS:")
    print("="*70)
    print("\n1. Read RENDER_DEPLOY_STEPS.md for detailed instructions")
    print("\n2. Quick deploy:")
    print("   a. Push code to GitHub")
    print("   b. Go to https://render.com")
    print("   c. New + → Blueprint → Select repo")
    print("   d. Render auto-configures from render.yaml")
    print("   e. Wait 10-12 minutes")
    print("   f. Access your public URL!")
    
    print("\n3. Manual deploy:")
    print("   - Follow detailed steps in RENDER_DEPLOY_STEPS.md")
    
    print("\n" + "="*70)
    print("📖 Read: RENDER_DEPLOY_STEPS.md")
    print("🌐 Visit: https://render.com")
    print("="*70 + "\n")

if __name__ == '__main__':
    main()
