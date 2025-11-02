# 🚀 Quick Start: Deploy to Render in 5 Minutes

This guide gets your Omi webhook running on Render.com as fast as possible.

## What You Need From Me

I need you to complete these steps:

---

## Step 1: Sign Up for Render (1 minute)

1. Go to https://render.com
2. Click **"Get Started for Free"**
3. Sign up with your **GitHub account** (easiest)
4. Verify your email

---

## Step 2: Deploy Your Webhook (2 minutes)

### Option A: One-Click Deploy with Blueprint (Recommended)

1. Go to Render Dashboard: https://dashboard.render.com
2. Click **"New"** → **"Blueprint"**
3. If asked, connect your GitHub account
4. Select your repository: **`vats98754/abracadabra`**
5. Click **"Apply"**

**That's it!** Render will automatically:
- Detect `render.yaml`
- Configure the service
- Start building

### Option B: Manual Setup

If Blueprint doesn't work:

1. Dashboard → **"New +"** → **"Web Service"**
2. Connect repository: **`vats98754/abracadabra`**
3. Configure:
   - **Name**: `omi-webhook`
   - **Branch**: `master`
   - **Runtime**: `Python 3`
   - **Build Command**:
     ```
     pip install -r requirements-webhook.txt && pip install -e . --no-deps && song_recogniser initialise || echo "DB init at runtime"
     ```
   - **Start Command**:
     ```
     uvicorn omi_song_recognition_webhook:app --host 0.0.0.0 --port $PORT
     ```
   - **Plan**: Free
4. Click **"Create Web Service"**

---

## Step 3: Add Environment Variables (2 minutes) ⚠️ CRITICAL

Before the service can work, you need to add your credentials:

1. In your Render service page, click **"Environment"** (left sidebar)
2. Click **"Add Environment Variable"**
3. Add these **one by one**:

### Copy These Exact Values:

```bash
# Required
OMI_APP_ID=01K8XC4TAWZCXNVZ2SXKBYC2HN
OMI_API_KEY=sk_ae93dd3fecc63dcd4501d7e0bb682607
OMI_USER_ID=zxajnHHxcpQDehlTZEnk3g3MNep2

# Optional but recommended
SUPABASE_URL=https://cekkrqnleagiizmrwvgn.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNla2tycW5sZWFnaWl6bXJ3dmduIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MTg3OTA0NCwiZXhwIjoyMDc3NDU1MDQ0fQ.6z2o72SjD9hz1q-ezhe__rPPAmaOmpko5GjkHIU8Cn8

# Default values (these are auto-configured in render.yaml, add manually if using Option B)
ABRACADABRA_PATH=/opt/render/project/src
MIN_AUDIO_LENGTH=10
MAX_BUFFER_DURATION=60
HOST=0.0.0.0
PYTHON_VERSION=3.11.0
```

4. Click **"Save Changes"**

**Important**: Render will automatically redeploy after you save the variables.

---

## Step 4: Verify Deployment (30 seconds)

Watch the **"Logs"** tab. You should see:

```
==> Building...
🚀 Building Omi Song Recognition Webhook for Render...
📦 Installing dependencies...
✅ Build complete!

==> Deploying...
INFO: Uvicorn running on http://0.0.0.0:10000
==> Your service is live 🎉
```

### Test Your Webhook

Once deployed, Render gives you a URL like: `https://omi-webhook.onrender.com`

Test it:
```bash
curl https://omi-webhook.onrender.com/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "service": "Omi Song Recognition",
  "active_users": 0
}
```

✅ **If you see this, your webhook is live!**

---

## What Happens Next?

After you complete these steps, tell me:

1. ✅ "Render deployment successful" - if the health check works
2. ❌ "Render deployment failed" - if you see errors (copy the error message)

Then we'll:
1. Configure your Omi app with the webhook URL
2. Register test songs in the database
3. Test end-to-end song recognition!

---

## Troubleshooting

### "Build failed"
- Check the Logs tab for errors
- Most common: Environment variables missing

### "502 Bad Gateway"
- Environment variables not set correctly
- Go to Environment tab and verify all required variables are added

### "Service not responding"
- Render free tier spins down after 15 minutes of inactivity
- First request takes ~30 seconds (cold start)
- This is normal and expected on free tier

---

## Summary

**What you need to do:**

1. ☐ Sign up at Render.com (1 min)
2. ☐ Create web service from GitHub repo (1 min)
3. ☐ Add environment variables (2 min)
4. ☐ Wait for deployment (2 min)
5. ☐ Test health endpoint (30 sec)

**Total time: ~5 minutes**

Once you've done this, come back and I'll help with the next steps!

---

## Your Webhook URL

After deployment, your webhook will be at:

**`https://omi-webhook.onrender.com`**

(or whatever name you chose)

You'll use this URL to configure your Omi device.

---

## Need Help?

Common issues and solutions are in **RENDER_SETUP.md**.

For detailed documentation, see:
- **RENDER_SETUP.md** - Complete guide with troubleshooting
- **NGROK_SETUP.md** - Local testing with ngrok

Ready? Go deploy! 🚀
