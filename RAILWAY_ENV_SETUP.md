# Quick Railway Environment Setup

## Method 1: Via Railway Dashboard (Easiest)

1. Go to https://railway.app/dashboard
2. Select your `shazomi-production` project
3. Click on your service
4. Go to the **Variables** tab
5. Click **Raw Editor** button
6. Paste the following and update with your actual values:

```bash
OMI_APP_ID=01K8XC4TAWZCXNVZ2SXKBYC2HN
OMI_API_KEY=sk_ae93dd3fecc63dcd4501d7e0bb682607
OMI_USER_ID=zxajnHHxcpQDehlTZEnk3g3MNep2
SUPABASE_URL=https://cekkrqnleagiizmrwvgn.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNla2tycW5sZWFnaWl6bXJ3dmduIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MTg3OTA0NCwiZXhwIjoyMDc3NDU1MDQ0fQ.6z2o72SjD9hz1q-ezhe__rPPAmaOmpko5GjkHIU8Cn8
ABRACADABRA_PATH=/app
MIN_AUDIO_LENGTH=10
MAX_BUFFER_DURATION=60
HOST=0.0.0.0
```

7. Click **Update Variables**
8. Railway will automatically redeploy with the new variables

## Method 2: Via Railway CLI

```bash
# Install Railway CLI if you haven't
npm install -g @railway/cli

# Login to Railway
railway login

# Link to your project
railway link

# Set environment variables (one at a time or from file)
railway variables set OMI_APP_ID=01K8XC4TAWZCXNVZ2SXKBYC2HN
railway variables set OMI_API_KEY=sk_ae93dd3fecc63dcd4501d7e0bb682607
railway variables set OMI_USER_ID=zxajnHHxcpQDehlTZEnk3g3MNep2
railway variables set SUPABASE_URL=https://cekkrqnleagiizmrwvgn.supabase.co
railway variables set SUPABASE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNla2tycW5sZWFnaWl6bXJ3dmduIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MTg3OTA0NCwiZXhwIjoyMDc3NDU1MDQ0fQ.6z2o72SjD9hz1q-ezhe__rPPAmaOmpko5GjkHIU8Cn8"
railway variables set ABRACADABRA_PATH=/app
railway variables set MIN_AUDIO_LENGTH=10
railway variables set MAX_BUFFER_DURATION=60
railway variables set HOST=0.0.0.0

# Trigger a redeploy
railway up
```

## Verify Git Integration

To ensure Railway auto-deploys on push:

1. Go to your Railway project settings
2. Check **Source** section
3. Verify it's connected to: `github.com/vats98754/abracadabra`
4. Verify branch is set to: `master`
5. **Auto Deploy** should be **Enabled**

If not connected:
1. Click **Connect Repo**
2. Select GitHub
3. Choose `vats98754/abracadabra` repository
4. Select `master` branch
5. Enable **Auto Deploy on Push**

## After Setting Variables

Once variables are set, Railway will automatically:
1. Rebuild the application
2. Run `start_webhook.sh` to initialize everything
3. Start the webhook server

Test the deployment:
```bash
curl https://shazomi-production.up.railway.app/health
```

Expected response:
```json
{"status":"healthy","service":"Omi Song Recognition","active_users":0}
```

## Next Steps

After Railway is running successfully:

1. **Register some songs** in the database (see RAILWAY_SETUP.md)
2. **Configure Omi app** with your webhook URL
3. **Test end-to-end** by playing music near your Omi device

---

**Note:** Railway provides the `PORT` environment variable automatically, so you don't need to set it manually.
