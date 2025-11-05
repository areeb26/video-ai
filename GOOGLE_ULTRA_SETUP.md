# Google Ultra Account Setup for Veo 3.1

How to connect your Google Ultra account to enable video generation.

---

## What You Need

- ✅ Google account with Ultra/Veo access
- ✅ Google AI API key
- ✅ Backend running locally

---

## Step 1: Get Your Google AI API Key

### Option A: Google AI Studio (Recommended)

1. **Go to Google AI Studio:**
   - Visit: https://aistudio.google.com/

2. **Sign in:**
   - Use your Google account with Ultra access

3. **Get API Key:**
   - Click **"Get API key"** button (top right)
   - Or go to: https://aistudio.google.com/app/apikey

4. **Create/Select Project:**
   - Click **"Create API key in new project"**
   - Or select existing project

5. **Copy API Key:**
   - Copy the key (starts with `AIza...`)
   - Save it somewhere safe!

### Option B: Google Cloud Console

1. **Go to Google Cloud Console:**
   - Visit: https://console.cloud.google.com/

2. **Create/Select Project:**
   - Click project dropdown (top left)
   - Create new project or select existing

3. **Enable APIs:**
   - Go to **APIs & Services** → **Library**
   - Search for **"Generative Language API"**
   - Click and **Enable**

4. **Create API Key:**
   - Go to **APIs & Services** → **Credentials**
   - Click **"Create Credentials"** → **"API key"**
   - Copy the generated key

---

## Step 2: Configure Backend

1. **Open backend `.env` file:**
```bash
cd backend
nano .env  # or use any text editor
```

2. **Add your API key:**
```env
# Google AI Configuration
GOOGLE_AI_API_KEY=AIzaSyC...your-actual-api-key-here

# Supabase Database
DATABASE_URL=postgresql://postgres:password@db.xxxxx.supabase.co:5432/postgres

# App Settings
SECRET_KEY=change-this-to-random-secret
DEBUG=True
ALLOWED_ORIGINS=http://localhost:3000
```

3. **Save and close** the file

---

## Step 3: Verify API Key Works

### Test with Backend API

1. **Start backend:**
```bash
cd backend
source venv/bin/activate
cd app
python main.py
```

2. **Test video generation:**
```bash
curl -X POST http://localhost:8000/api/v1/generation \
  -H "Content-Type: application/json" \
  -d '{
    "generation_type": "text_to_video",
    "prompt": "A person walking in a park on a sunny day",
    "aspect_ratio": "16:9",
    "quality": "low"
  }'
```

3. **Check response:**

**✅ Success:**
```json
{
  "id": 1,
  "status": "processing",
  "prompt": "A person walking in a park on a sunny day",
  "veo_job_id": "veo_xxxxx"
}
```

**❌ Error (Invalid API Key):**
```json
{
  "status": "failed",
  "error_message": "Invalid API key"
}
```

**❌ Error (No Veo Access):**
```json
{
  "status": "failed",
  "error_message": "Permission denied. Veo API not available."
}
```

---

## Step 4: Check Veo Access

### Verify You Have Veo 3.1 Access

Veo 3.1 is currently in limited preview. To check if you have access:

1. **Go to Google Labs:**
   - Visit: https://labs.google/veo

2. **Sign in with your Google account**

3. **Check status:**
   - ✅ If you have access: You'll see "Try Veo"
   - ❌ If no access: You'll see "Request access"

### Request Veo Access

If you don't have access yet:

1. **Fill out waitlist form:**
   - Visit: https://labs.google/veo
   - Click **"Request access"**
   - Fill in the form

2. **Alternative - Google AI Test Kitchen:**
   - Visit: https://aitestkitchen.withgoogle.com/
   - Request access to experimental features

3. **Wait for approval:**
   - Usually takes 1-2 weeks
   - You'll get email when approved

---

## What Works Without Veo Access

While waiting for Veo access, these features still work:

✅ **Character Management:**
- Create character profiles
- Upload face references
- Face embedding extraction
- Outfit management

✅ **Project Planning:**
- Create projects
- Build timelines with beats
- Create shot lists
- Camera path planning

✅ **API Testing:**
- All API endpoints work
- Database operations
- File uploads

❌ **Video Generation:**
- Won't work without Veo API access
- Will return error message

---

## Using Your Ultra Account

### With Google One Ultra

If you have **Google One Ultra** subscription:

1. **Benefits:**
   - Access to Gemini Ultra model
   - Priority access to new features
   - May include Veo preview access

2. **Check your access:**
   - Sign in to Google AI Studio
   - Look for available models
   - Check for Veo/video generation options

3. **API Key:**
   - Same process as above
   - Use Google AI Studio to get API key
   - Your subscription benefits apply automatically

---

## API Key Security

### Best Practices

**✅ DO:**
- Keep API key in `.env` file (never in code)
- Use different keys for dev/production
- Rotate keys periodically
- Restrict API key to specific APIs

**❌ DON'T:**
- Commit `.env` to Git (it's already in .gitignore)
- Share API key publicly
- Use same key across multiple projects
- Hardcode in source code

### Restrict API Key (Recommended)

1. **Go to Google Cloud Console:**
   - https://console.cloud.google.com/apis/credentials

2. **Click on your API key**

3. **Add restrictions:**
   - **Application restrictions:** HTTP referrers or IP addresses
   - **API restrictions:** Select "Restrict key" → "Generative Language API"

4. **Save**

---

## Quota and Limits

### Free Tier (Google AI Studio)

- **Rate limits:**
  - 60 requests per minute
  - 1,500 requests per day

- **When you hit limit:**
  - Wait 1 minute before next request
  - Or upgrade to paid tier

### Paid Tier (Google Cloud)

- **Higher limits:**
  - 10,000+ requests per minute
  - Pay per use

- **Cost:**
  - Check current pricing at: https://ai.google.dev/pricing

---

## Troubleshooting

### Issue: "Invalid API key"

**Solutions:**
1. Check for extra spaces in `.env`
2. Ensure key starts with `AIza`
3. Verify key is active in Google Cloud Console
4. Regenerate key if needed

### Issue: "Permission denied"

**Causes:**
- API not enabled in Google Cloud
- Veo API not available for your account
- API key restrictions too strict

**Solutions:**
1. Enable Generative Language API in Cloud Console
2. Check if you have Veo access
3. Remove API restrictions temporarily

### Issue: "Quota exceeded"

**Solutions:**
1. Wait 1 minute (for rate limit)
2. Wait until tomorrow (for daily limit)
3. Upgrade to paid tier
4. Use multiple API keys (not recommended)

### Issue: "API key not working in app"

**Check:**
1. `.env` file is in `backend/` directory
2. No quotes around API key in `.env`
3. Restart backend after changing `.env`
4. Check backend logs for errors

---

## Environment Variables Format

### Correct Format

```env
# ✅ Correct
GOOGLE_AI_API_KEY=AIzaSyC1234567890abcdefg

# ❌ Wrong - no quotes!
GOOGLE_AI_API_KEY="AIzaSyC1234567890abcdefg"

# ❌ Wrong - no spaces!
GOOGLE_AI_API_KEY = AIzaSyC1234567890abcdefg
```

---

## Testing Video Generation

### Simple Test

```bash
# Create a character
curl -X POST http://localhost:8000/api/v1/characters \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Character", "age": 25}'

# Generate video
curl -X POST http://localhost:8000/api/v1/generation \
  -H "Content-Type: application/json" \
  -d '{
    "generation_type": "text_to_video",
    "prompt": "A person smiling at camera in bright room",
    "aspect_ratio": "16:9",
    "quality": "low",
    "character_id": 1
  }'

# Check status (replace 1 with generation ID)
curl http://localhost:8000/api/v1/generation/1
```

### Using the UI

1. **Start frontend:**
```bash
cd frontend
npm run dev
```

2. **Go to Generation page:**
   - http://localhost:3000/generation

3. **Enter prompt and generate:**
   - Type: "A person walking in a sunny park"
   - Select aspect ratio: 16:9
   - Click "Generate Video"

4. **Monitor status:**
   - Watch generation status in UI
   - Check backend logs for progress

---

## Multiple Google Accounts

If you have multiple Google accounts:

### Use Different API Keys

```env
# Development
GOOGLE_AI_API_KEY=AIzaSyC...dev-key...

# Production (different account)
# GOOGLE_AI_API_KEY=AIzaSyC...prod-key...
```

### Switch Between Accounts

1. Generate API key from each account
2. Comment/uncomment in `.env`
3. Restart backend

---

## Production Setup

### For Deployed App

1. **Use environment variables:**
   - Not `.env` file
   - Set in hosting platform

2. **Examples:**

**Vercel:**
```bash
vercel env add GOOGLE_AI_API_KEY
# Paste your API key when prompted
```

**Railway:**
```bash
railway variables set GOOGLE_AI_API_KEY=AIzaSyC...
```

**Heroku:**
```bash
heroku config:set GOOGLE_AI_API_KEY=AIzaSyC...
```

**Docker:**
```yaml
environment:
  - GOOGLE_AI_API_KEY=AIzaSyC...
```

---

## Summary Checklist

- [ ] Signed in to Google account with Ultra access
- [ ] Got API key from Google AI Studio
- [ ] Added API key to `backend/.env`
- [ ] No quotes or spaces in `.env`
- [ ] Restarted backend server
- [ ] Tested video generation
- [ ] Checked Veo access status
- [ ] API key restrictions configured (optional)

---

## Quick Reference

**Get API Key:**
- https://aistudio.google.com/app/apikey

**Check Veo Access:**
- https://labs.google/veo

**Google Cloud Console:**
- https://console.cloud.google.com/

**Pricing Info:**
- https://ai.google.dev/pricing

---

## Next Steps

Once your API key is configured:

1. ✅ Backend will use your Ultra account
2. ✅ Generate videos with Veo 3.1
3. ✅ Character consistency will work
4. ✅ All features enabled

Start creating! 🚀
