# 🚀 Render Deployment Guide for OpenFactVerification

## 📋 Pre-Deployment Checklist

Your app is now **deployment-ready** for Render! Here's what's been configured:

### ✅ Files Added/Updated:
- `render_app.py` - Production entry point
- `Procfile` - Tells Render how to start your app
- `build.sh` - Installs dependencies during deployment
- `api_config_production.yaml` - Production config template
- `requirements.txt` - Updated with all dependencies

## 🔧 Render Setup Instructions

### 1. **Create Render Account**
- Go to [render.com](https://render.com)
- Sign up with your GitHub account

### 2. **Connect GitHub Repository**
- Push your code to: `https://github.com/himanshusdeshmukh2106/fake-new-detection.git`
- In Render dashboard: "New" → "Web Service"
- Connect your GitHub repository

### 3. **Configure Render Settings**

**Build & Deploy:**
- **Environment:** `Python 3`
- **Build Command:** `./build.sh`
- **Start Command:** `python render_app.py`
- **Branch:** `main`

**Environment Variables (CRITICAL):**
Add these in Render's Environment Variables section:

```

```

### 4. **Optional GCS Settings** (if you want cloud storage later):
```
GCS_BUCKET_NAME=your-bucket-name
GCS_BASE_URL=https://storage.googleapis.com/your-bucket-name
GOOGLE_APPLICATION_CREDENTIALS={"type": "service_account", ...}
```

## 🎯 What Happens During Deployment

1. **Build Phase:**
   - Installs Python dependencies
   - Downloads spaCy language model
   - Sets up Playwright for web scraping

2. **Runtime:**
   - Loads environment variables for API keys
   - Uses local file processing (no GCS required)
   - Handles image/video uploads temporarily
   - Serves on Render's assigned port

## 🔒 Security Features

- ✅ API keys stored as environment variables (not in code)
- ✅ Production config separate from development
- ✅ Sensitive files excluded from git
- ✅ No persistent file storage (privacy-focused)

## 🚀 Deployment Steps

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Ready for Render deployment"
   git push origin main
   ```

2. **Create Render Service:**
   - Connect GitHub repo
   - Set environment variables
   - Deploy!

3. **First Deploy:**
   - Takes ~5-10 minutes (installing dependencies)
   - Subsequent deploys are faster

## 🧪 Testing Your Deployment

Once deployed, test these features:
- ✅ Text fact-checking
- ✅ Image upload and analysis
- ✅ Video upload and analysis
- ✅ Claims extraction with visual filtering

## 🔧 Troubleshooting

**Common Issues:**

1. **Build Fails:**
   - Check build logs in Render dashboard
   - Ensure `build.sh` has execute permissions

2. **App Won't Start:**
   - Verify environment variables are set
   - Check start command: `python render_app.py`

3. **API Errors:**
   - Confirm SERPER_API_KEY and GEMINI_API_KEY are valid
   - Check Render logs for specific error messages

## 💡 Cost Estimation

**Render Free Tier:**
- ✅ 750 hours/month (enough for continuous running)
- ✅ Automatic builds from GitHub
- ✅ HTTPS included
- ❌ Sleeps after 15min inactivity (cold starts)

**Render Starter ($7/month):**
- ✅ No sleeping
- ✅ Faster builds
- ✅ Better performance

## 🎯 Your App is Ready!

All configurations are complete. Your fact-checking app will:
- Process text, images, and videos
- Extract only factual claims (no visual descriptions)
- Work reliably without external storage dependencies
- Scale automatically on Render

**Next Step:** Push to GitHub and deploy on Render! 🚀