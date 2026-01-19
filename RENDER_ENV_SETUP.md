# Render.com Deployment - Environment Variables Setup

## Required Environment Variables

After your deployment is created on Render, you need to add these environment variables:

### 1. GROQ_API_KEY (For Translation Feature)
- Go to your Render dashboard
- Select your **smart-doc-extractor** service
- Click on **Environment** tab
- Add new environment variable:
  - **Key**: `GROQ_API_KEY`
  - **Value**: `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`

### Auto-configured Variables
These are automatically set by render.yaml:
- ✅ `SECRET_KEY` - Auto-generated secure key
- ✅ `DATABASE_URL` - PostgreSQL connection string
- ✅ `FLASK_ENV` - Set to production
- ✅ `FLASK_CONFIG` - Set to config_production.ProductionConfig

## Deployment Steps

1. **Go to Render Dashboard**: https://dashboard.render.com
2. **Click "New +" → "Blueprint"**
3. **Connect GitHub and select**: `smart-doc-extractor`
4. **Render will detect** `render.yaml` automatically
5. **Click "Apply"** to start deployment
6. **Add GROQ_API_KEY** in Environment tab (see above)
7. **Wait 10-15 minutes** for build and deployment
8. **Your app will be live!**

## Key Features of This Deployment

✅ **Lightweight**: Uses only Tesseract OCR (fits in free tier 512MB RAM)  
✅ **PostgreSQL Database**: Free tier with persistent storage  
✅ **SSL/HTTPS**: Automatic secure connection  
✅ **Auto-deploys**: Updates automatically on git push  
✅ **Health Checks**: Automatic restart if service fails  

## Deployment URL
Your app will be available at:
**https://smart-doc-extractor.onrender.com**

## Troubleshooting

### If deployment fails:
1. Check build logs in Render dashboard
2. Verify all environment variables are set
3. Make sure GROQ_API_KEY is added
4. Check that build.sh has execute permissions

### If app is slow to start:
- Free tier services sleep after 15 minutes of inactivity
- First request after sleep takes 30-60 seconds
- Subsequent requests are fast

## Monitoring
- View logs: Render Dashboard → Logs tab
- Check metrics: Render Dashboard → Metrics tab
- Set up alerts: Render Dashboard → Settings → Notifications
