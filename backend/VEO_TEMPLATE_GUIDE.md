# Veo Request Template Customization Guide

This guide explains how to customize the Veo API request template.

---

## Template File Location

```
backend/veo_request_template.json
```

This JSON file contains the **exact request format** sent to the Veo 3.1 API.

---

## Default Template

```json
{
  "clientContext": {
    "projectId": "b4aac356-f762-46e3-99dc-0feee5c15e8f",
    "tool": "PINHOLE",
    "userPaygateTier": "PAYGATE_TIER_TWO"
  },
  "requests": [
    {
      "aspectRatio": "VIDEO_ASPECT_RATIO_LANDSCAPE",
      "seed": 17274,
      "textInput": {
        "prompt": "{{PROMPT}}"
      },
      "videoModelKey": "veo_3_1_t2v_fast_ultra",
      "metadata": {
        "sceneId": "d4cb909e-26e9-4032-8223-600a687f541a"
      }
    }
  ]
}
```

---

## Available Placeholders

The template supports these placeholders (automatically replaced):

- `{{PROMPT}}` - Your video prompt
- `{{ASPECT_RATIO}}` - Video aspect ratio
- `{{SEED}}` - Random seed for generation
- `{{MODEL_KEY}}` - Veo model key
- `{{SCENE_ID}}` - Unique scene identifier

**Note:** These are optional - values in requests array are overridden by the code.

---

## How to Customize

### 1. Change Project ID

Edit the `projectId` in `clientContext`:

```json
"clientContext": {
  "projectId": "YOUR_PROJECT_ID_HERE",
  "tool": "PINHOLE",
  "userPaygateTier": "PAYGATE_TIER_TWO"
}
```

### 2. Change Tool

```json
"tool": "PINHOLE"  // or "WEB", "MOBILE", etc.
```

### 3. Change Paygate Tier

```json
"userPaygateTier": "PAYGATE_TIER_TWO"  // TIER_TWO = Ultra account
// Other options: "PAYGATE_TIER_ONE", "PAYGATE_TIER_THREE"
```

### 4. Add Additional Fields

You can add any custom fields from your n8n workflow:

```json
{
  "clientContext": {
    "projectId": "b4aac356-f762-46e3-99dc-0feee5c15e8f",
    "tool": "PINHOLE",
    "userPaygateTier": "PAYGATE_TIER_TWO",
    "customField": "customValue"  // ✅ Add custom fields
  },
  "requests": [
    {
      "aspectRatio": "VIDEO_ASPECT_RATIO_LANDSCAPE",
      "seed": 17274,
      "textInput": {
        "prompt": "{{PROMPT}}"
      },
      "videoModelKey": "veo_3_1_t2v_fast_ultra",
      "metadata": {
        "sceneId": "d4cb909e-26e9-4032-8223-600a687f541a"
      },
      "customParam": "value"  // ✅ Add custom parameters
    }
  ]
}
```

---

## Copying from n8n Workflow

### Step 1: Get JSON from n8n

1. Open your n8n workflow
2. Click on the **"Veo api"** node
3. Go to **"Body"** → **"JSON"**
4. Copy the entire JSON object

### Step 2: Replace Template

1. Open `backend/veo_request_template.json`
2. Paste your n8n JSON
3. Replace dynamic values with placeholders:
   - Replace the prompt with `"{{PROMPT}}"`
   - Keep other values as-is

### Step 3: Restart Backend

```bash
# Stop backend (Ctrl+C)
# Restart
cd backend/app
python main.py
```

The template is loaded when the service starts!

---

## Example: Full Customization

Let's say your n8n workflow has this JSON:

```json
{
  "clientContext": {
    "projectId": "my-custom-project",
    "tool": "MY_TOOL",
    "userPaygateTier": "PAYGATE_TIER_THREE",
    "userId": "user123",
    "sessionId": "session456"
  },
  "requests": [
    {
      "aspectRatio": "VIDEO_ASPECT_RATIO_PORTRAIT",
      "seed": 99999,
      "textInput": {
        "prompt": "My video prompt",
        "language": "en",
        "style": "cinematic"
      },
      "videoModelKey": "veo_3_1_t2v_fast_ultra",
      "metadata": {
        "sceneId": "custom-scene-id",
        "tags": ["test", "demo"]
      },
      "duration": 5
    }
  ]
}
```

**Save it to `veo_request_template.json`:**

```json
{
  "clientContext": {
    "projectId": "my-custom-project",
    "tool": "MY_TOOL",
    "userPaygateTier": "PAYGATE_TIER_THREE",
    "userId": "user123",
    "sessionId": "session456"
  },
  "requests": [
    {
      "aspectRatio": "VIDEO_ASPECT_RATIO_PORTRAIT",
      "seed": 99999,
      "textInput": {
        "prompt": "{{PROMPT}}",
        "language": "en",
        "style": "cinematic"
      },
      "videoModelKey": "veo_3_1_t2v_fast_ultra",
      "metadata": {
        "sceneId": "custom-scene-id",
        "tags": ["test", "demo"]
      },
      "duration": 5
    }
  ]
}
```

**Restart backend** and all requests will use this template! ✅

---

## What Gets Overridden

Even if you set these in the template, they'll be overridden by the code:

- `seed` - Always random (10000-99999)
- `aspectRatio` - Based on API request
- `videoModelKey` - Based on generation type (t2v/i2v/v2v)
- `textInput.prompt` - Your actual prompt
- `metadata.sceneId` - Generated from seed

**Everything else** stays as you set it in the template!

---

## Testing Your Template

### Check What's Being Sent

The API response includes `request_sent` field:

```bash
curl -X POST http://localhost:8000/api/v1/generation \
  -H "Content-Type: application/json" \
  -d '{
    "generation_type": "text_to_video",
    "prompt": "A test video",
    "aspect_ratio": "16:9",
    "quality": "low"
  }' | jq .request_sent
```

This shows the exact JSON sent to Veo API!

---

## Multiple Templates

Want different templates for different use cases?

**Option 1: Swap Template Files**

```bash
# Save different versions
cp veo_request_template.json veo_template_standard.json
cp veo_template_custom.json veo_request_template.json
# Restart backend
```

**Option 2: Environment Variable (Future)**

We can add support for multiple templates via config later.

---

## Common Customizations

### Change Default Seed Range

Edit `backend/app/services/veo_service.py` line 73:

```python
seed = random.randint(10000, 99999)  # Change range here
```

### Add More Placeholders

Edit `veo_service.py` lines 79-84 to add your own:

```python
request_str = request_str.replace("{{MY_PLACEHOLDER}}", "my_value")
```

### Skip Placeholder Replacement

If you want template used exactly as-is, remove lines 78-85 in `veo_service.py`.

---

## Troubleshooting

### "File not found" Error

**Check path:**
```bash
ls backend/veo_request_template.json
```

**Should exist!** If not, create it from this guide.

### Changes Not Applied

**Restart backend:**
- Template is loaded on service startup
- Changes require restart
- Stop (Ctrl+C) and run `./start.sh` again

### Invalid JSON

**Validate your JSON:**
```bash
cat backend/veo_request_template.json | jq .
```

If error, fix JSON syntax.

---

## Best Practices

**DO:**
- ✅ Keep a backup: `cp veo_request_template.json veo_template_backup.json`
- ✅ Validate JSON before saving
- ✅ Test with simple prompt first
- ✅ Check `request_sent` in response
- ✅ Document your changes

**DON'T:**
- ❌ Remove required fields (clientContext, requests)
- ❌ Change template while backend is running
- ❌ Put sensitive data in template (use .env instead)

---

## Example: Updating from n8n

**Your n8n workflow changed? Update in 3 steps:**

```bash
# 1. Copy new JSON from n8n
# 2. Save to backend/veo_request_template.json
# 3. Restart backend
./start.sh
```

That's it! ✨

---

## Summary

- **Template file:** `backend/veo_request_template.json`
- **Edit anytime:** Just edit the JSON file
- **Apply changes:** Restart backend
- **Test:** Check `request_sent` in API response
- **Customize freely:** Add any fields from your n8n workflow

You have full control over the API request format! 🎉
