# Railway Deployment Guide for Omi Song Recognition Webhook

This guide explains how to deploy the Omi song recognition webhook to Railway.

## Prerequisites

- Railway account with project set up to track this repository
- Omi app credentials (APP_ID and API_KEY)
- Supabase account (optional, if you want to store results)

## Step 1: Configure Environment Variables

In your Railway project dashboard, go to the **Variables** tab and add the following environment variables:

### Required Variables

```bash
# Omi App Credentials
OMI_APP_ID=your_app_id_here
OMI_API_KEY=your_api_key_here
OMI_USER_ID=your_user_id_here

# Server Settings (Railway provides PORT automatically)
HOST=0.0.0.0
```

### Optional Variables

```bash
# Abracadabra Settings
ABRACADABRA_PATH=/app
MIN_AUDIO_LENGTH=10
MAX_BUFFER_DURATION=60

# Supabase (if you want to store recognition results)
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_service_role_key
```

## Step 2: Deployment

Railway automatically deploys when you push to the `master` branch. The deployment process:

1. **Build**: Railway installs dependencies from `requirements.txt`
2. **Setup**: `start_webhook.sh` runs to:
   - Install abracadabra package (without PyAudio)
   - Initialize the song database
   - Start the uvicorn server

## Step 3: Verify Deployment

Once deployed, Railway will provide a public URL (e.g., `https://shazomi-production.up.railway.app`).

Test the health endpoint:

```bash
curl https://your-app.up.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "Omi Song Recognition",
  "active_users": 0
}
```

## Step 4: Configure Omi App Webhook

1. Open the Omi mobile app
2. Go to **Developer Mode** settings
3. Enable **Real-time Audio Streaming**
4. Set webhook URL to: `https://your-app.up.railway.app/audio`
5. Save settings

## Step 5: Add Songs to Database

Before the webhook can recognize songs, you need to register them in the database.

### Option A: Register via API (Recommended for Production)

Create a separate script or endpoint to register songs:

```python
import subprocess

def register_song(audio_file_path):
    cmd = ['song_recogniser', 'register', audio_file_path]
    subprocess.run(cmd, check=True)
```

### Option B: Register Locally and Upload Database

1. Register songs locally:
   ```bash
   song_recogniser register path/to/song.mp3
   ```

2. Upload the `abracadabra.db` file to Railway:
   - Use Railway CLI or volume mounts
   - Or create a registration endpoint in the webhook

## Troubleshooting

### 502 Bad Gateway Error

**Possible causes:**
- Environment variables not set
- Database not initialized
- PyAudio installation failing (should be skipped in `start_webhook.sh`)

**Solution:**
Check Railway logs:
```bash
railway logs
```

### Song Recognition Not Working

**Possible causes:**
- No songs registered in database
- Audio quality too low
- Audio duration too short

**Solution:**
- Check `/stats/{uid}` endpoint to see buffer duration
- Ensure MIN_AUDIO_LENGTH is appropriate (default: 10 seconds)
- Verify songs are registered with metadata

### Notifications Not Sending

**Possible causes:**
- OMI_APP_ID or OMI_API_KEY incorrect
- Omi API endpoint changed
- User ID mismatch

**Solution:**
- Verify credentials in Railway environment variables
- Check webhook logs for notification errors
- Test notification API directly:
  ```bash
  curl -X POST "https://api.omi.me/v2/integrations/{APP_ID}/notification?uid={UID}&message=Test" \
    -H "Authorization: Bearer {API_KEY}"
  ```

## Monitoring

### Health Check

```bash
curl https://your-app.up.railway.app/health
```

### User Stats

```bash
curl https://your-app.up.railway.app/stats/{user_id}
```

### Clear User Buffer

```bash
curl -X DELETE https://your-app.up.railway.app/buffer/{user_id}
```

## Scaling Considerations

For production use:

1. **Database**: Consider using PostgreSQL instead of SQLite for better concurrency
2. **File Storage**: Store temporary WAV files in object storage (S3, R2) instead of local filesystem
3. **Processing**: Move song recognition to background workers for better performance
4. **Caching**: Cache recognition results to avoid duplicate processing
5. **Rate Limiting**: Add rate limiting to prevent abuse

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OMI_APP_ID` | Yes | - | Your Omi app ID from h.omi.me/apps |
| `OMI_API_KEY` | Yes | - | Your Omi API key for authentication |
| `OMI_USER_ID` | Optional | - | Default user ID for testing |
| `HOST` | No | 0.0.0.0 | Server bind address |
| `PORT` | No | 8000 | Server port (Railway sets this automatically) |
| `ABRACADABRA_PATH` | No | /app | Path to abracadabra installation |
| `MIN_AUDIO_LENGTH` | No | 10 | Minimum seconds of audio before recognition |
| `MAX_BUFFER_DURATION` | No | 60 | Maximum buffer size in seconds |
| `SUPABASE_URL` | Optional | - | Supabase project URL |
| `SUPABASE_KEY` | Optional | - | Supabase service role key |

## Support

For issues or questions:
- Check Railway logs: `railway logs`
- Review Omi developer docs: https://docs.omi.me/
- Check abracadabra repository: https://github.com/notexactlyawe/abracadabra
