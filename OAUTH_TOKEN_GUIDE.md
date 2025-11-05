# How to Get OAuth Bearer Token for Veo 3.1

This guide shows you how to get the OAuth bearer token needed for Veo 3.1 API access.

---

## What is a Bearer Token?

A bearer token is an OAuth 2.0 access token that authenticates API requests. It's required for the Google AI Sandbox Veo 3.1 API.

**Token Format:** `ya29.a0ATi6K2...` (starts with `ya29`)

---

## Method 1: Using Google Cloud Console (Recommended)

### Step 1: Enable Required APIs

1. Go to **Google Cloud Console**: https://console.cloud.google.com
2. Select your project (or create new one)
3. Go to **APIs & Services** → **Library**
4. Search and enable:
   - **Generative Language API**
   - **AI Platform API**

### Step 2: Create OAuth 2.0 Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **"Create Credentials"** → **"OAuth client ID"**
3. If prompted, configure OAuth consent screen first:
   - Choose **"External"** (for testing)
   - Fill in app name and your email
   - Add your email as test user
   - Save

4. For Application type, choose **"Desktop app"** or **"Web application"**
5. Click **"Create"**
6. Download the JSON file (client_secret.json)

### Step 3: Get Access Token

**Option A: Using gcloud CLI (Easiest)**

```bash
# Install gcloud if not already installed
# Visit: https://cloud.google.com/sdk/docs/install

# Login
gcloud auth login

# Get access token
gcloud auth print-access-token
```

Copy the token that starts with `ya29...`

**Option B: Using OAuth Playground**

1. Go to: https://developers.google.com/oauthplayground
2. Click gear icon (⚙️) → Check **"Use your own OAuth credentials"**
3. Enter your OAuth Client ID and Client Secret
4. In **Step 1**: Select **"AI Platform API v1"** or manually enter:
   ```
   https://www.googleapis.com/auth/cloud-platform
   ```
5. Click **"Authorize APIs"**
6. Sign in with your Google account
7. In **Step 2**: Click **"Exchange authorization code for tokens"**
8. Copy the **"Access token"** (starts with `ya29...`)

**Option C: Using Python Script**

```python
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Download client_secret.json from Google Cloud Console first

SCOPES = ['https://www.googleapis.com/auth/cloud-platform']

flow = InstalledAppFlow.from_client_secrets_file(
    'client_secret.json', SCOPES)

creds = flow.run_local_server(port=0)

print("Access Token:")
print(creds.token)
```

Run:
```bash
pip install google-auth-oauthlib
python get_token.py
```

---

## Method 2: From Your n8n Workflow (Quick)

Since you already have a working n8n workflow:

1. Open your n8n workflow
2. Look at the **"Veo api"** node
3. Click on the node → Headers
4. The **Authorization** header contains your bearer token
5. Copy everything after `"Bearer "` (the `ya29...` part)

---

## Method 3: Service Account (For Production)

For automated/production use:

### Step 1: Create Service Account

1. Go to **IAM & Admin** → **Service Accounts**
2. Click **"Create Service Account"**
3. Name it (e.g., "veo-api-service")
4. Grant role: **"Vertex AI User"** or **"AI Platform Admin"**
5. Click **"Done"**

### Step 2: Create Key

1. Click on the service account
2. Go to **"Keys"** tab
3. Click **"Add Key"** → **"Create new key"**
4. Choose **JSON** format
5. Download the JSON key file

### Step 3: Get Token from Service Account

```python
from google.oauth2 import service_account
from google.auth.transport.requests import Request

# Load service account credentials
credentials = service_account.Credentials.from_service_account_file(
    'service-account-key.json',
    scopes=['https://www.googleapis.com/auth/cloud-platform']
)

# Get access token
credentials.refresh(Request())
print("Access Token:")
print(credentials.token)
```

---

## Configure Backend

Once you have your bearer token:

### Option 1: Edit `.env` Directly

```bash
cd backend
nano .env
```

Add:
```env
GOOGLE_AI_BEARER_TOKEN=ya29.your_actual_token_here
VEO_PROJECT_ID=your-project-id
```

### Option 2: Or Use API Key (Simpler)

If you just have an API key:
```env
GOOGLE_AI_API_KEY=AIzaSyC...your_api_key
```

The backend will use bearer token if available, otherwise falls back to API key.

---

## Token Expiration

**Important:** Bearer tokens expire!

- **User tokens:** Expire after 1 hour
- **Service account tokens:** Expire after 1 hour
- **Refresh tokens:** Last longer, used to get new access tokens

### Auto-Refresh Solution

For production, implement token refresh:

```python
# backend/app/services/token_manager.py
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from datetime import datetime, timedelta

class TokenManager:
    def __init__(self, service_account_file):
        self.credentials = service_account.Credentials.from_service_account_file(
            service_account_file,
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )
        self.token = None
        self.expiry = None

    def get_token(self):
        # Refresh if expired or about to expire
        if not self.token or datetime.now() >= self.expiry - timedelta(minutes=5):
            self.credentials.refresh(Request())
            self.token = self.credentials.token
            self.expiry = self.credentials.expiry

        return self.token
```

---

## Verify Token Works

Test your token:

```bash
curl -X POST https://aisandbox-pa.googleapis.com/v1/video:batchAsyncGenerateVideoText \
  -H "Authorization: Bearer ya29.YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "clientContext": {
      "projectId": "your-project-id",
      "tool": "PINHOLE",
      "userPaygateTier": "PAYGATE_TIER_TWO"
    },
    "requests": [{
      "aspectRatio": "VIDEO_ASPECT_RATIO_LANDSCAPE",
      "seed": 12345,
      "textInput": {"prompt": "A person walking in a park"},
      "videoModelKey": "veo_3_1_t2v_fast_ultra",
      "metadata": {"sceneId": "test-scene"}
    }]
  }'
```

**Success:** Returns JSON with video generation job
**Error:** Check token expiration or permissions

---

## Get Your Project ID

Your Google Cloud Project ID is needed for API requests.

**Find it:**
1. Go to **Google Cloud Console**: https://console.cloud.google.com
2. Look at top bar - next to "Google Cloud"
3. Click project dropdown
4. Your project ID is shown below project name

Or use:
```bash
gcloud config get-value project
```

---

## Security Best Practices

**DO:**
- ✅ Use service accounts for production
- ✅ Store tokens in `.env` (not in code)
- ✅ Rotate tokens regularly
- ✅ Use short-lived tokens
- ✅ Implement token refresh

**DON'T:**
- ❌ Commit tokens to Git (`.env` is in .gitignore)
- ❌ Share tokens publicly
- ❌ Use same token across environments
- ❌ Hardcode tokens in source code

---

## Troubleshooting

### "Invalid authentication credentials"

**Solutions:**
- Token expired (get new one)
- Wrong token format (should start with `ya29`)
- Missing scopes (add cloud-platform scope)

### "Permission denied"

**Solutions:**
- Enable required APIs in Cloud Console
- Add proper roles to service account
- Check if you have Veo access

### "Token expired"

**Solutions:**
- Get new token (user tokens last 1 hour)
- Implement auto-refresh with service account
- Use refresh token to get new access token

---

## Quick Start Summary

**Fastest method:**

1. Install gcloud: https://cloud.google.com/sdk/docs/install
2. Run: `gcloud auth login`
3. Run: `gcloud auth print-access-token`
4. Copy token to `backend/.env`:
   ```env
   GOOGLE_AI_BEARER_TOKEN=ya29.your_token_here
   VEO_PROJECT_ID=your-project-id
   ```
5. Done! Start backend and it will use your token

---

## Need Help?

- **Google Cloud Docs**: https://cloud.google.com/docs/authentication
- **OAuth Playground**: https://developers.google.com/oauthplayground
- **gcloud Auth**: https://cloud.google.com/sdk/gcloud/reference/auth

---

## Next Steps

Once configured:
1. Backend uses your token automatically
2. Generate videos through API
3. Token refreshes handled for service accounts
4. Check logs if authentication fails

The app is now connected to real Veo 3.1 API! 🎉
