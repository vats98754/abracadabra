# Using ngrok for Omi Webhook (Free Testing)

ngrok is perfect for testing the webhook before deploying to production.

## Step 1: Sign up for ngrok (Free)

1. Go to https://dashboard.ngrok.com/signup
2. Sign up (takes 30 seconds)
3. Get your authtoken: https://dashboard.ngrok.com/get-started/your-authtoken

## Step 2: Configure ngrok

```bash
ngrok config add-authtoken YOUR_TOKEN_HERE
```

## Step 3: Start Your Local Webhook

```bash
# In terminal 1
source venv/bin/activate
python omi_song_recognition_webhook.py
```

The webhook will start on `http://localhost:8000`

## Step 4: Start ngrok Tunnel

```bash
# In terminal 2
ngrok http 8000
```

You'll see output like:
```
Forwarding    https://abc123.ngrok-free.app -> http://localhost:8000
```

## Step 5: Configure Omi App

1. Copy the HTTPS URL (e.g., `https://abc123.ngrok-free.app`)
2. Open Omi app → Developer Mode
3. Enable Real-time Audio Streaming
4. Set webhook URL: `https://abc123.ngrok-free.app/audio`
5. Save

## Step 6: Test!

Play a song near your Omi device and watch the terminal logs!

## Pros of ngrok

- ✅ Instant setup (no deployment wait)
- ✅ See real-time logs in your terminal
- ✅ Easy debugging
- ✅ Free tier includes HTTPS
- ✅ Perfect for testing before production

## Cons of ngrok

- ❌ URL changes every time you restart (unless you pay)
- ❌ Must keep computer running
- ❌ Not for production use
- ❌ Free tier has bandwidth limits

## For Production

Once you've tested with ngrok and everything works, deploy to:
- **Render.com** (easiest)
- **Fly.io** (best performance)
- **Deta Space** (simplest)
- **Railway** (what we configured)

## ngrok Free Tier Limits

- 1 online ngrok process
- 40 connections/minute
- Random URLs (unless paid)
- Perfect for testing!

## Commands Reference

```bash
# Start webhook
source venv/bin/activate
python omi_song_recognition_webhook.py

# Start ngrok (in another terminal)
ngrok http 8000

# View web interface
# Open http://localhost:4040 in browser to see all requests!
```

The ngrok web interface at `http://localhost:4040` shows:
- All incoming requests
- Request/response details
- Perfect for debugging!
