# Render.com Deployment Guide for Omi Song Recognition Webhook

Complete guide to deploy your Omi webhook on Render's free tier.

## Why Render?

- ✅ **Free tier** - 750 hours/month (enough for hobby projects)
- ✅ **Auto-deploy** - Automatically deploys on git push
- ✅ **HTTPS** - Free SSL certificates
- ✅ **Custom domains** - Add your own domain
- ✅ **Easy setup** - 5-minute deployment

## Prerequisites

- GitHub account with `abracadabra` repository
- Render account (free - sign up at https://render.com)
- Omi app credentials (you already have these in `.env`)

---

## Step 1: Sign Up for Render

1. Go to https://render.com
2. Click **"Get Started for Free"**
3. Sign up with GitHub (recommended) or email
4. Verify your email

---

## Step 2: Create New Web Service

### Option A: Using Blueprint (Easiest - One Click Deploy)

1. Go to your Render Dashboard: https://dashboard.render.com
2. Click **"New"** → **"Blueprint"**
3. Connect your GitHub account if not already connected
4. Select repository: **`vats98754/abracadabra`**
5. Click **"Apply"**
6. Render will automatically detect `render.yaml` and configure everything!

**Jump to Step 3** to add environment variables.

### Option B: Manual Setup

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Click **"Connect a repository"**
4. Authorize Render to access your GitHub
5. Select repository: **`vats98754/abracadabra`**
6. Configure the service:

**Basic Settings:**
- **Name**: `omi-webhook` (or any name you prefer)
- **Region**: Choose closest to you (e.g., `Oregon (US West)`)
- **Branch**: `master`
- **Runtime**: `Python 3`

**Build Settings:**
- **Build Command**:
  ```bash
  pip install -r requirements-webhook.txt && pip install -e . --no-deps && song_recogniser initialise || echo "DB init at runtime"
  ```

- **Start Command**:
  ```bash
  uvicorn omi_song_recognition_webhook:app --host 0.0.0.0 --port $PORT
  ```

**Instance Settings:**
- **Plan**: `Free` (automatically selected)
- **Health Check Path**: `/health`

7. Click **"Advanced"** to set Python version:
   - Add environment variable: `PYTHON_VERSION` = `3.11.0`

---

## Step 3: Add Environment Variables (CRITICAL)

Before deploying, add your environment variables:

1. In your web service page, go to **"Environment"** tab (left sidebar)
2. Click **"Add Environment Variable"**
3. Add each of these variables:

### Required Variables (Copy from Your `.env` File)

```bash
OMI_APP_ID=01K8XC4TAWZCXNVZ2SXKBYC2HN
OMI_API_KEY=sk_ae93dd3fecc63dcd4501d7e0bb682607
OMI_USER_ID=zxajnHHxcpQDehlTZEnk3g3MNep2
```

### Optional but Recommended

```bash
SUPABASE_URL=https://cekkrqnleagiizmrwvgn.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNla2tycW5sZWFnaWl6bXJ3dmduIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MTg3OTA0NCwiZXhwIjoyMDc3NDU1MDQ0fQ.6z2o72SjD9hz1q-ezhe__rPPAmaOmpko5GjkHIU8Cn8
```

### Default Values (Auto-configured)

```bash
ABRACADABRA_PATH=/opt/render/project/src
MIN_AUDIO_LENGTH=10
MAX_BUFFER_DURATION=60
HOST=0.0.0.0
PYTHON_VERSION=3.11.0
```

**Note**: Render automatically provides the `PORT` variable, so you don't need to add it.

4. Click **"Save Changes"**

---

## Step 4: Deploy

If using **Blueprint** (Option A), deployment starts automatically after adding variables.

If using **Manual Setup** (Option B):
1. Click **"Create Web Service"** at the bottom
2. Render will start building and deploying (takes 3-5 minutes)

### Watch the Build Process

You'll see real-time logs:
```
==> Building...
🚀 Building Omi Song Recognition Webhook for Render...
📦 Installing dependencies...
📦 Installing abracadabra package...
🗄️  Initializing database...
✅ Build complete!

==> Deploying...
INFO:     Started server process
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:10000

==> Your service is live 🎉
```

---

## Step 5: Get Your Webhook URL

Once deployed, Render provides a URL:

**Format**: `https://omi-webhook.onrender.com`

You'll see it at the top of your service page.

---

## Step 6: Test the Deployment

Test the health endpoint:

```bash
curl https://omi-webhook.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "Omi Song Recognition",
  "active_users": 0
}
```

✅ **If you see this, your webhook is live!**

---

## Step 7: Configure Omi App

1. Open the **Omi mobile app**
2. Go to **Settings** → **Developer Mode** (or wherever webhook settings are)
3. Enable **"Real-time Audio Streaming"**
4. Set **Webhook URL**: `https://omi-webhook.onrender.com/audio`
5. **Save** settings

---

## Step 8: Register Songs (Important!)

The webhook needs songs in its database to recognize them.

### Option A: Upload Your Local Database

If you have songs registered locally (you do!):

1. Go to Render Dashboard → Your Service
2. Click **"Shell"** tab (opens a terminal)
3. Run:
   ```bash
   # Your local database has songs, but Render starts fresh
   # You need to re-register songs
   ```

### Option B: Create Registration Endpoint (Recommended)

Add songs via API by modifying the webhook to include a registration endpoint.

### Option C: Register via Shell

1. Go to **Shell** tab in Render
2. Register songs:
   ```bash
   song_recogniser register /path/to/song.mp3
   ```

For now, you'll need to upload songs to Render or create a registration API.

---

## Step 9: Test End-to-End

1. Play a **registered song** near your Omi device
2. Wait at least **10 seconds** (MIN_AUDIO_LENGTH)
3. Check Render logs: **"Logs"** tab
4. You should see:
   ```
   INFO - Received X bytes from user {uid}
   INFO - User {uid} buffer: 10.5 seconds of audio
   INFO - Attempting song recognition...
   INFO - Song recognized: {'artist': '...', 'title': '...'}
   INFO - ✅ Notification sent successfully
   ```
5. Check your **Omi app** for the notification!

---

## Monitoring & Debugging

### View Logs

Render Dashboard → Your Service → **"Logs"** tab

See real-time logs of:
- Incoming audio streams
- Recognition attempts
- Notifications sent
- Errors

### Check Service Status

Dashboard shows:
- **Green dot** = Running
- **Red dot** = Failed
- **Yellow dot** = Building/Deploying

### Metrics

**"Metrics"** tab shows:
- CPU usage
- Memory usage
- Request count
- Response times

---

## Important Notes

### Free Tier Limitations

⚠️ **Render's free tier spins down after 15 minutes of inactivity**

- **What this means**: First request after inactivity takes ~30 seconds (cold start)
- **Impact**: First audio stream might miss the beginning
- **Solution**:
  - Upgrade to paid tier ($7/month for always-on)
  - Or accept the cold start delay
  - Or use ngrok for development/testing

### Disk Storage

- Render's free tier has **persistent disk disabled**
- Your `abracadabra.db` will reset on every deploy
- **Solution**:
  - Use external database (Supabase - already configured!)
  - Or upgrade to paid tier for persistent disk
  - Or register songs via API on startup

---

## Troubleshooting

### Build Failed: "PyAudio installation error"

✅ **Already fixed!** We use `requirements-webhook.txt` which excludes PyAudio.

If you still see this:
- Check build command uses `requirements-webhook.txt`
- Check it includes `--no-deps` flag

### Deployment Succeeded But 502 Error

**Cause**: Missing environment variables

**Fix**:
1. Go to **Environment** tab
2. Verify all required variables are set
3. Click **"Manual Deploy"** → **"Clear build cache & deploy"**

### Recognition Not Working

**Cause**: No songs in database

**Fix**:
1. Check logs for "Song recognized" messages
2. Verify songs are registered (see Step 8)
3. Check audio duration is >= MIN_AUDIO_LENGTH

### Notifications Not Sending

**Cause**: Incorrect Omi credentials or API endpoint

**Fix**:
1. Verify `OMI_APP_ID` and `OMI_API_KEY` are correct
2. Check logs for notification errors
3. Test notification API directly:
   ```bash
   curl -X POST "https://api.omi.me/v2/integrations/01K8XC4TAWZCXNVZ2SXKBYC2HN/notification?uid=test&message=Test" \
     -H "Authorization: Bearer sk_ae93dd3fecc63dcd4501d7e0bb682607"
   ```

---

## Auto-Deploy on Git Push

Render automatically deploys when you push to `master` branch!

```bash
# Make changes
git add .
git commit -m "Update webhook"
git push origin master

# Render detects push and deploys automatically
# Watch progress in Render Dashboard → Logs
```

---

## Upgrading to Paid Tier (Optional)

If you need 24/7 uptime and persistent storage:

**Starter Plan** - $7/month
- No cold starts
- Always running
- Persistent disk (10GB)
- Custom domains
- More CPU/RAM

---

## Support & Resources

- **Render Docs**: https://render.com/docs
- **Render Status**: https://status.render.com
- **Support**: https://render.com/support
- **Community**: https://community.render.com

---

## Quick Reference

| Aspect | Details |
|--------|---------|
| **Service URL** | `https://omi-webhook.onrender.com` |
| **Health Check** | `https://omi-webhook.onrender.com/health` |
| **Logs** | Dashboard → Logs tab |
| **Environment Variables** | Dashboard → Environment tab |
| **Shell Access** | Dashboard → Shell tab |
| **Redeploy** | Dashboard → Manual Deploy button |

---

## Next Steps

✅ Service deployed on Render
✅ Environment variables configured
✅ Health check passing
⬜ Register songs in database
⬜ Configure Omi app webhook URL
⬜ Test end-to-end recognition

---

**Your webhook is ready! 🎉**

Configure your Omi device to use `https://omi-webhook.onrender.com/audio` and start recognizing songs!
