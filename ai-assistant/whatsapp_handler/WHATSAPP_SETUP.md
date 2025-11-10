# WhatsApp Web Integration - Setup Guide

Complete guide for setting up WhatsApp Web automation with the AI Assistant.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Initial Setup](#initial-setup)
4. [Testing](#testing)
5. [Usage Examples](#usage-examples)
6. [Troubleshooting](#troubleshooting)
7. [Security](#security)

---

## Prerequisites

### Required Software

1. **Google Chrome Browser**
   ```bash
   # Ubuntu/Debian
   wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
   sudo dpkg -i google-chrome-stable_current_amd64.deb

   # macOS
   brew install --cask google-chrome
   ```

2. **ChromeDriver** (automatically managed by webdriver-manager)

3. **Python Dependencies**
   ```bash
   pip install selenium webdriver-manager pywhatkit
   ```

### WhatsApp Requirements

- Active WhatsApp account on your phone
- Phone connected to internet
- WhatsApp app installed and logged in

---

## Installation

### Step 1: Install Dependencies

```bash
cd ai-assistant
pip install -r requirements.txt
```

### Step 2: Configure Environment

Edit `.env` file:

```env
# WhatsApp Settings
WHATSAPP_ENABLED=True
WHATSAPP_METHOD=selenium
WHATSAPP_HEADLESS=False
WHATSAPP_DEFAULT_COUNTRY_CODE=+92
WHATSAPP_AUTO_START_QUEUE=False

# Add authorized numbers (optional)
WHATSAPP_AUTHORIZED_NUMBERS=+923001234567,+923007654321
```

---

## Initial Setup

### Step 1: Start the Assistant

```bash
python main.py
```

### Step 2: Initialize WhatsApp

**Option A: Via API**

```bash
curl -X POST http://localhost:8001/api/v1/whatsapp/initialize
```

**Option B: Via Web Interface**

1. Open http://localhost:8001/docs
2. Navigate to `/whatsapp/initialize` endpoint
3. Click "Try it out" and "Execute"

### Step 3: Scan QR Code

1. A Chrome browser window will open
2. WhatsApp Web will load with a QR code
3. Open WhatsApp on your phone:
   - Android: Menu → Linked Devices → Link a Device
   - iPhone: Settings → Linked Devices → Link a Device
4. Scan the QR code displayed in the browser
5. Wait for "Login successful!" message

**Screenshots:**

```
┌─────────────────────────┐
│  WhatsApp Web           │
│                         │
│  ┌─────────────────┐   │
│  │                 │   │
│  │   QR CODE HERE  │   │  ← Scan this with your phone
│  │                 │   │
│  └─────────────────┘   │
│                         │
│ Keep WhatsApp open on  │
│ your phone              │
└─────────────────────────┘
```

### Step 4: Verify Connection

```bash
curl http://localhost:8001/api/v1/whatsapp/status
```

Expected response:
```json
{
  "is_logged_in": true,
  "session_valid": true,
  "session_stats": {...},
  "queue_stats": {...}
}
```

---

## Testing

### Test 1: Send a Message

```bash
curl -X POST http://localhost:8001/api/v1/whatsapp/send \
  -H "Content-Type: application/json" \
  -d '{
    "number": "+923001234567",
    "message": "Test message from AI Assistant!",
    "language": "en",
    "method": "selenium"
  }'
```

### Test 2: Send an Urdu Message

```bash
curl -X POST http://localhost:8001/api/v1/whatsapp/send \
  -H "Content-Type: application/json" \
  -d '{
    "number": "+923001234567",
    "message": "یہ AI Assistant سے ایک ٹیسٹ پیغام ہے!",
    "language": "ur",
    "method": "selenium"
  }'
```

### Test 3: Schedule a Message

```bash
curl -X POST http://localhost:8001/api/v1/whatsapp/schedule \
  -H "Content-Type: application/json" \
  -d '{
    "number": "+923001234567",
    "message": "Scheduled reminder",
    "delay_minutes": 5,
    "language": "en"
  }'
```

### Test 4: Send a File

```bash
curl -X POST http://localhost:8001/api/v1/whatsapp/send-file \
  -H "Content-Type: application/json" \
  -d '{
    "number": "+923001234567",
    "file_path": "/path/to/file.pdf",
    "caption": "Here is the document",
    "language": "en"
  }'
```

---

## Usage Examples

### Example 1: Task Reminder via WhatsApp

```python
import requests

# Create a task
task_response = requests.post(
    "http://localhost:8001/api/v1/tasks",
    json={
        "title": "Call the client",
        "priority": "high",
        "language": "en"
    }
)

# Send WhatsApp notification
whatsapp_response = requests.post(
    "http://localhost:8001/api/v1/whatsapp/send",
    json={
        "number": "+923001234567",
        "message": "New task created: Call the client (High Priority)",
        "language": "en"
    }
)
```

### Example 2: Natural Language Commands

Via the assistant endpoint:

```bash
# English
curl -X POST http://localhost:8001/api/v1/assistant \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Send a WhatsApp to +923001234567 saying Hello",
    "language": "en"
  }'

# Urdu
curl -X POST http://localhost:8001/api/v1/assistant \
  -H "Content-Type: application/json" \
  -d '{
    "message": "واٹس ایپ پیغام بھیجیں +923001234567 کو کہ سلام",
    "language": "ur"
  }'
```

### Example 3: Start Queue Worker for Scheduled Messages

```bash
curl -X POST http://localhost:8001/api/v1/whatsapp/start-queue-worker
```

---

## Troubleshooting

### Issue 1: QR Code Not Appearing

**Problem:** Browser opens but QR code doesn't show

**Solutions:**
1. Check internet connection
2. Clear browser cache and try again
3. Use a different Chrome profile:
   ```bash
   # Delete session directory
   rm -rf ~/.ai-assistant/whatsapp-session
   # Restart initialization
   ```

### Issue 2: "Not logged in" Error

**Problem:** API returns "Not logged in to WhatsApp"

**Solutions:**
1. Check session status:
   ```bash
   curl http://localhost:8001/api/v1/whatsapp/status
   ```

2. Reconnect:
   ```bash
   curl -X POST http://localhost:8001/api/v1/whatsapp/reconnect
   ```

3. Re-initialize if needed:
   ```bash
   curl -X POST http://localhost:8001/api/v1/whatsapp/initialize
   ```

### Issue 3: Messages Not Sending

**Problem:** API returns success but message doesn't send

**Solutions:**
1. Check health:
   ```bash
   curl -X POST http://localhost:8001/api/v1/whatsapp/health-check
   ```

2. Verify phone number format:
   - Must include country code
   - Format: +[country code][number]
   - Example: +923001234567

3. Check browser window is not minimized
4. Ensure WhatsApp Web is not logged out

### Issue 4: Session Expires

**Problem:** Have to scan QR code repeatedly

**Solutions:**
1. Don't delete session directory (`~/.ai-assistant/whatsapp-session`)
2. Don't log out from WhatsApp Web manually
3. Keep browser window open (can minimize)
4. Check session validity:
   ```bash
   curl http://localhost:8001/api/v1/whatsapp/status
   ```

### Issue 5: Chrome Driver Issues

**Problem:** "chromedriver" not found or version mismatch

**Solutions:**
1. Update webdriver-manager:
   ```bash
   pip install --upgrade webdriver-manager
   ```

2. Manually clear cache:
   ```bash
   rm -rf ~/.wdm
   ```

3. Ensure Chrome is up to date:
   ```bash
   google-chrome --version
   ```

---

## Security

### Authorized Numbers

Only allow specific numbers to control the assistant:

1. **Add authorized number:**
   ```bash
   curl -X POST http://localhost:8001/api/v1/whatsapp/authorize \
     -H "Content-Type: application/json" \
     -d '{"number": "+923001234567"}'
   ```

2. **List authorized numbers:**
   ```bash
   curl http://localhost:8001/api/v1/whatsapp/authorized
   ```

3. **Remove authorized number:**
   ```bash
   curl -X DELETE http://localhost:8001/api/v1/whatsapp/authorize/+923001234567
   ```

### Best Practices

1. **Don't share session files:**
   - Keep `~/.ai-assistant/whatsapp-session` private
   - Don't commit session files to git

2. **Use environment variables:**
   - Store authorized numbers in `.env`
   - Don't hardcode phone numbers in code

3. **Rate limiting:**
   - Don't send too many messages quickly
   - WhatsApp may temporarily block the account

4. **Backup session:**
   - Periodically backup session directory
   - Allows quick recovery if session is lost

### WhatsApp Terms of Service

**Important:**
- WhatsApp Web automation may violate WhatsApp's Terms of Service
- Use this for personal automation only
- Do NOT use for:
  - Spam or bulk messaging
  - Commercial purposes without permission
  - Automated marketing
- WhatsApp may ban accounts that violate ToS

---

## Advanced Configuration

### Headless Mode

Run browser in background (no window):

```env
WHATSAPP_HEADLESS=True
```

**Note:** Headless mode requires session to be already initialized with QR scan.

### Custom Session Directory

```env
WHATSAPP_SESSION_DIR=/custom/path/to/session
```

### Auto-start Queue Worker

Automatically process scheduled messages on startup:

```env
WHATSAPP_AUTO_START_QUEUE=True
```

### Queue Check Interval

How often to check for scheduled messages (seconds):

```env
WHATSAPP_QUEUE_CHECK_INTERVAL=30
```

---

## N8N Integration

### Setup N8N Workflows

1. Import workflows from `n8n_workflows/` directory:
   - `whatsapp_notification.json` - Send notifications
   - `whatsapp_task_reminder.json` - Daily task reminders

2. Configure webhook URLs in N8N to match your assistant URL

3. Test workflows:
   ```bash
   curl -X POST http://localhost:5678/webhook/whatsapp-notify \
     -H "Content-Type: application/json" \
     -d '{
       "data": {
         "phone_number": "+923001234567",
         "message": "Test from N8N"
       },
       "language": "en"
     }'
   ```

---

## Support

### Resources

- [API Documentation](http://localhost:8001/docs)
- [WhatsApp Web.js](https://github.com/pedroslopez/whatsapp-web.js/)
- [Selenium Documentation](https://selenium-python.readthedocs.io/)

### Getting Help

1. Check logs for errors
2. Test with simple messages first
3. Verify session is active
4. Check network connectivity
5. Review this guide's troubleshooting section

---

## Next Steps

1. ✅ Complete initial setup and QR scan
2. ✅ Send test messages
3. ✅ Configure authorized numbers
4. ✅ Set up N8N workflows
5. ✅ Create automated task reminders
6. ✅ Integrate with your workflows

Happy automating! 🚀📱
