# ✅ Final Setup & Testing Guide

Your Omi webhook is LIVE at: **`https://omi-webhook.onrender.com`**

## Current Status

✅ Webhook deployed and running on Render
✅ Health check passing: `https://omi-webhook.onrender.com/health`
✅ API endpoints available: `/audio`, `/register`, `/songs`, `/health`
⏳ Need to: Register songs + Configure Omi app + Test

---

## Step 1: Register a Test Song (Choose One Method)

### Option A: Upload via API (Easiest)

Use this curl command to upload a song from your computer:

```bash
cd /Users/anvayvats/abracadabra

curl -X POST "https://omi-webhook.onrender.com/register" \
  -F "file=@dataset/downloads/Confess - Confess - Army of Pigs! (Single Version) - pXNftK5z4Gs.wav" \
  -F "artist=Confess" \
  -F "title=Army of Pigs"
```

This will:
- Upload the audio file
- Extract fingerprints
- Store in the database
- Return success message

### Option B: Use Render Shell

1. Go to https://dashboard.render.com
2. Click on your `omi-webhook` service
3. Click **"Shell"** tab (opens terminal)
4. Run:
   ```bash
   # You'll need to upload a song file first or register from a URL
   # For now, use Option A above which is easier
   ```

### Verify Songs Are Registered

```bash
curl https://omi-webhook.onrender.com/songs
```

Expected response:
```json
{
  "status": "success",
  "count": 1,
  "songs": [
    {"artist": "Confess", "album": null, "title": "Army of Pigs"}
  ]
}
```

---

## Step 2: Configure Your Omi Device

### In the Omi Mobile App:

1. Open the Omi app on your phone
2. Go to **Settings** or **Developer Mode**
3. Look for **"Webhooks"** or **"Integrations"** or **"Audio Streaming"**
4. Enable **"Real-time Audio Streaming"**
5. Set the webhook URL to:
   ```
   https://omi-webhook.onrender.com/audio
   ```
6. Save settings

**Note**: The exact location varies by Omi app version. Look for:
- "Developer Settings"
- "Webhook Configuration"
- "Audio Streaming Settings"
- "App Integration URL"

---

## Step 3: Test End-to-End

### Test the Full Flow:

1. **Play the registered song** near your Omi device
   - Use Spotify, YouTube, or play the audio file
   - Make sure your Omi device is on and recording

2. **Wait 10+ seconds** (MIN_AUDIO_LENGTH setting)
   - The webhook accumulates audio before attempting recognition

3. **Check Render logs** to see what's happening:
   - Go to Render Dashboard → Your Service → **"Logs"** tab
   - You should see:
     ```
     INFO - Received X bytes from user {uid}
     INFO - User {uid} buffer: 10.5 seconds of audio
     INFO - Attempting song recognition...
     INFO - Song recognized: {'artist': 'Confess', 'title': 'Army of Pigs', ...}
     INFO - ✅ Notification sent successfully
     ```

4. **Check your Omi app** for the notification!
   - You should receive a message like:
     > 🎵 You're listening to: 'Army of Pigs' by Confess

---

## Step 4: Test the Webhook Manually (Optional)

You can test the recognition without your Omi device:

### Create Test Audio Stream:

```bash
# Convert a small clip to raw PCM and send to webhook
ffmpeg -i "dataset/downloads/Confess - Confess - Army of Pigs! (Single Version) - pXNftK5z4Gs.wav" \
  -f s16le -acodec pcm_s16le -ar 16000 -ac 1 -t 15 test_audio.raw

# Send to webhook (replace YOUR_USER_ID)
curl -X POST "https://omi-webhook.onrender.com/audio?sample_rate=16000&uid=YOUR_USER_ID" \
  --data-binary "@test_audio.raw" \
  -H "Content-Type: application/octet-stream"
```

---

## Troubleshooting

### Issue: "No songs recognized"

**Possible causes:**
- No songs in database
- Audio quality too low
- Audio duration too short (<10 seconds)

**Solutions:**
- Verify songs are registered: `curl https://omi-webhook.onrender.com/songs`
- Check Render logs for recognition scores
- Increase audio buffer duration

### Issue: "Notification not received"

**Possible causes:**
- OMI_APP_ID or OMI_API_KEY incorrect
- Notification API endpoint changed
- User ID mismatch

**Solutions:**
- Verify credentials in Render environment variables
- Check Render logs for notification errors
- Try with your actual OMI_USER_ID: `zxajnHHxcpQDehlTZEnk3g3MNep2`

### Issue: "Webhook not receiving audio"

**Possible causes:**
- Omi app not configured correctly
- Webhook URL typo
- Omi device not streaming

**Solutions:**
- Double-check webhook URL in Omi app
- Verify Omi device is on and recording
- Check Render logs to see if ANY requests are coming in

### Issue: "502 Bad Gateway" or "Service Offline"

**Possible causes:**
- Render free tier spins down after 15 min inactivity
- Cold start in progress

**Solutions:**
- First request takes ~30 seconds to wake up (this is normal)
- Check health endpoint: `curl https://omi-webhook.onrender.com/health`
- Wait and try again

---

## Monitoring

### View Real-Time Logs:

1. Go to https://dashboard.render.com
2. Click on `omi-webhook` service
3. Click **"Logs"** tab
4. Watch logs in real-time as audio streams in

### Check Service Status:

```bash
# Health check
curl https://omi-webhook.onrender.com/health

# User statistics (after sending some audio)
curl https://omi-webhook.onrender.com/stats/YOUR_USER_ID

# List registered songs
curl https://omi-webhook.onrender.com/songs
```

---

## Adding More Songs

### Upload Multiple Songs:

```bash
# Song 1
curl -X POST "https://omi-webhook.onrender.com/register" \
  -F "file=@song1.mp3" \
  -F "artist=Artist Name" \
  -F "title=Song Title"

# Song 2
curl -X POST "https://omi-webhook.onrender.com/register" \
  -F "file=@song2.mp3" \
  -F "artist=Another Artist" \
  -F "title=Another Song"
```

### Batch Upload Script:

```bash
#!/bin/bash
for file in dataset/downloads/*.wav; do
  # Extract metadata from filename pattern: Artist - Title
  filename=$(basename "$file" .wav)
  artist=$(echo "$filename" | cut -d'-' -f1 | xargs)
  title=$(echo "$filename" | cut -d'-' -f2 | xargs)

  echo "Registering: $artist - $title"
  curl -X POST "https://omi-webhook.onrender.com/register" \
    -F "file=@$file" \
    -F "artist=$artist" \
    -F "title=$title"

  sleep 2  # Don't overwhelm the server
done
```

---

## Important Notes

### Render Free Tier Limitations:

⚠️ **Cold starts**: Service spins down after 15 minutes of inactivity
- First request after inactivity takes ~30 seconds
- This is normal and expected on free tier
- Upgrade to $7/month for always-on service

⚠️ **No persistent disk**: Database resets on every deploy
- Need to re-register songs after each deployment
- Solution: Use external database (Supabase is already configured!)
- Or create a startup script that auto-registers songs

### Omi Device Audio Format:

- **Sample rate**: 16kHz (DevKit2) or 8kHz (older devices)
- **Format**: 16-bit PCM, mono, raw audio bytes
- **Streaming**: Continuous real-time stream while recording

---

## What's Next?

Once you've completed the steps above and tested successfully:

1. ✅ Register your favorite songs
2. ✅ Configure Omi app with webhook URL
3. ✅ Test recognition with registered songs
4. ✅ Enjoy real-time song recognition!

### Future Enhancements:

- Add more songs to expand recognition library
- Set up persistent database (Supabase integration)
- Add song history tracking
- Create playlist generation based on listening habits
- Add Spotify/Apple Music integration
- Deploy to production with always-on hosting

---

## Quick Command Reference

```bash
# Register a song
curl -X POST "https://omi-webhook.onrender.com/register" \
  -F "file=@song.mp3" -F "artist=Artist" -F "title=Title"

# List all songs
curl https://omi-webhook.onrender.com/songs

# Health check
curl https://omi-webhook.onrender.com/health

# User stats
curl https://omi-webhook.onrender.com/stats/YOUR_USER_ID

# Clear user buffer
curl -X DELETE https://omi-webhook.onrender.com/buffer/YOUR_USER_ID

# View API docs
open https://omi-webhook.onrender.com/docs
```

---

🎉 **Your Omi song recognition webhook is ready!**

Any issues? Check the Render logs first - they show everything that's happening in real-time.
