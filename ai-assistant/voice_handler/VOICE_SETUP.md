# Voice Commands - Setup Guide

Complete guide for setting up voice command features with the AI Assistant.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Initial Setup](#initial-setup)
4. [Testing](#testing)
5. [Usage Examples](#usage-examples)
6. [Wake Words](#wake-words)
7. [Troubleshooting](#troubleshooting)
8. [Advanced Configuration](#advanced-configuration)

---

## Prerequisites

### Required Software

1. **Python 3.8+**
   ```bash
   python --version
   ```

2. **Audio System**
   - Working microphone
   - Audio output (speakers/headphones)
   - System audio drivers installed

### Platform-Specific Requirements

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install -y portaudio19-dev python3-pyaudio
sudo apt-get install -y espeak espeak-data libespeak-dev
sudo apt-get install -y flac
```

#### macOS
```bash
brew install portaudio
brew install espeak
```

#### Windows
- PyAudio wheel installation required
- Download from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
```bash
pip install PyAudio-0.2.11-cp39-cp39-win_amd64.whl
```

---

## Installation

### Step 1: Install Python Dependencies

```bash
cd ai-assistant
pip install -r requirements.txt
```

### Step 2: Verify PyAudio Installation

```bash
python -c "import pyaudio; print('PyAudio installed successfully!')"
```

If this fails, see [Troubleshooting](#troubleshooting) section.

### Step 3: Configure Environment

Edit `.env` file:

```env
# Voice Integration
VOICE_ENABLED=True
VOICE_WAKE_WORD_REQUIRED=True
VOICE_WAKE_WORDS=hey assistant,اے اسسٹنٹ
VOICE_CONTINUOUS_MODE=False
VOICE_RESPONSE_ENABLED=True
VOICE_SPEECH_RATE=150
VOICE_VOLUME=0.9
VOICE_ENERGY_THRESHOLD=4000
VOICE_TIMEOUT=5
VOICE_PHRASE_TIME_LIMIT=10
VOICE_AUTO_CALIBRATE=True
```

---

## Initial Setup

### Step 1: Start the Assistant

```bash
python main.py
```

The API will be available at `http://localhost:8001`

### Step 2: Test Microphone Access

**Via API:**
```bash
curl -X POST http://localhost:8001/api/v1/voice/test/microphone
```

Expected response:
```json
{
  "microphone_available": true,
  "device_count": 3,
  "default_device": "Built-in Microphone",
  "message": "Microphone test successful"
}
```

**Via Web Interface:**
1. Open http://localhost:8001/docs
2. Navigate to `/voice/test/microphone` endpoint
3. Click "Try it out" and "Execute"

### Step 3: Calibrate Microphone

Calibration adjusts for ambient noise:

```bash
curl -X POST http://localhost:8001/api/v1/voice/calibrate \
  -H "Content-Type: application/json" \
  -d '{"duration": 3}'
```

Response:
```json
{
  "energy_threshold": 4200,
  "message": "Microphone calibrated successfully"
}
```

**Instructions:**
- Stay quiet during calibration
- Let it measure background noise
- Threshold is automatically set

### Step 4: Test Text-to-Speech

```bash
curl -X POST http://localhost:8001/api/v1/voice/test/tts \
  -H "Content-Type: application/json" \
  -d '{"language": "en"}'
```

You should hear: "Voice test successful. This is a test in English."

Test in Urdu:
```bash
curl -X POST http://localhost:8001/api/v1/voice/test/tts \
  -H "Content-Type: application/json" \
  -d '{"language": "ur"}'
```

---

## Testing

### Test 1: Speech Recognition

**English:**
```bash
curl -X POST http://localhost:8001/api/v1/voice/recognize \
  -H "Content-Type: application/json" \
  -d '{
    "language": "en",
    "timeout": 5
  }'
```

Then speak clearly into your microphone. You'll get:
```json
{
  "recognized_text": "what you said",
  "language": "en",
  "confidence": 0.95
}
```

**Urdu:**
```bash
curl -X POST http://localhost:8001/api/v1/voice/recognize \
  -H "Content-Type: application/json" \
  -d '{
    "language": "ur",
    "timeout": 5
  }'
```

### Test 2: Text-to-Speech

**English:**
```bash
curl -X POST http://localhost:8001/api/v1/voice/speak \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, this is a test message.",
    "language": "en"
  }'
```

**Urdu:**
```bash
curl -X POST http://localhost:8001/api/v1/voice/speak \
  -H "Content-Type: application/json" \
  -d '{
    "text": "سلام، یہ ایک ٹیسٹ پیغام ہے۔",
    "language": "ur"
  }'
```

### Test 3: Voice Command with Assistant

```bash
curl -X POST http://localhost:8001/api/v1/voice/command \
  -H "Content-Type: application/json" \
  -d '{
    "language": "en",
    "timeout": 5,
    "respond_with_voice": true
  }'
```

Then say: **"Create a task to buy groceries"**

The assistant will:
1. Recognize your speech
2. Process the command
3. Create the task
4. Speak the response

### Test 4: Background Listener

**Start listening:**
```bash
curl -X POST http://localhost:8001/api/v1/voice/listener/start \
  -H "Content-Type: application/json" \
  -d '{"continuous": true}'
```

**Check status:**
```bash
curl http://localhost:8001/api/v1/voice/listener/status
```

Response:
```json
{
  "is_running": true,
  "continuous_mode": true,
  "wake_word_required": true,
  "commands_processed": 0,
  "last_activity": "2025-11-10T12:30:45"
}
```

**Stop listening:**
```bash
curl -X POST http://localhost:8001/api/v1/voice/listener/stop
```

---

## Usage Examples

### Example 1: Voice Task Creation

**Scenario:** Create a task using voice command

```python
import requests

# Start voice recognition
response = requests.post(
    "http://localhost:8001/api/v1/voice/command",
    json={
        "language": "en",
        "timeout": 5,
        "respond_with_voice": True
    }
)

# Say: "Create a task to call the dentist tomorrow"

print(response.json())
# Output: {
#   "recognized_text": "create a task to call the dentist tomorrow",
#   "response": "Task created successfully: Call the dentist tomorrow",
#   "language": "en"
# }
```

### Example 2: Bilingual Voice Commands

**English command:**
```bash
# Say: "What are my pending tasks?"
curl -X POST http://localhost:8001/api/v1/voice/command \
  -H "Content-Type: application/json" \
  -d '{"language": "en", "respond_with_voice": true}'
```

**Urdu command:**
```bash
# Say: "میرے زیر التوا کام کیا ہیں؟"
curl -X POST http://localhost:8001/api/v1/voice/command \
  -H "Content-Type: application/json" \
  -d '{"language": "ur", "respond_with_voice": true}'
```

### Example 3: Continuous Voice Mode

**Start continuous listening:**
```python
import requests

# Start listener
response = requests.post(
    "http://localhost:8001/api/v1/voice/listener/start",
    json={"continuous": True}
)

print("Listening... Say 'Hey Assistant' followed by your command")

# The listener will:
# 1. Wait for wake word: "Hey Assistant"
# 2. Listen for command after wake word
# 3. Process command with assistant
# 4. Speak the response
# 5. Continue listening for next wake word
```

### Example 4: Custom Wake Word

**Add a custom wake word:**
```bash
curl -X POST http://localhost:8001/api/v1/voice/wake-word/add \
  -H "Content-Type: application/json" \
  -d '{
    "wake_word": "computer",
    "language": "en"
  }'
```

**List all wake words:**
```bash
curl http://localhost:8001/api/v1/voice/wake-words
```

Response:
```json
{
  "wake_words": {
    "en": ["hey assistant", "ok assistant", "hello assistant", "computer"],
    "ur": ["اے اسسٹنٹ", "ہیلو اسسٹنٹ", "سلام اسسٹنٹ"]
  }
}
```

### Example 5: Voice with WhatsApp Integration

```python
import requests

# Start voice command
response = requests.post(
    "http://localhost:8001/api/v1/voice/command",
    json={
        "language": "en",
        "timeout": 10,
        "respond_with_voice": True
    }
)

# Say: "Send a WhatsApp message to +923001234567 saying Hello"

# The assistant will:
# 1. Recognize: "send a whatsapp message to +923001234567 saying hello"
# 2. Extract number and message
# 3. Send WhatsApp message
# 4. Respond: "WhatsApp message sent successfully"
```

### Example 6: File Operations via Voice

```bash
# Say: "Create a file called notes.txt with content Hello World"
curl -X POST http://localhost:8001/api/v1/voice/command \
  -H "Content-Type: application/json" \
  -d '{"language": "en", "respond_with_voice": true}'
```

---

## Wake Words

### Default Wake Words

**English:**
- "Hey Assistant"
- "OK Assistant"
- "Hello Assistant"

**Urdu:**
- "اے اسسٹنٹ" (Ae Assistant)
- "ہیلو اسسٹنٹ" (Hello Assistant)
- "سلام اسسٹنٹ" (Salam Assistant)

### How Wake Words Work

1. **Continuous Mode:**
   - Listener waits for wake word
   - Only processes commands after wake word detected
   - Prevents accidental command execution

2. **Wake Word Detection:**
   ```
   User: "Hey Assistant, what's the weather?"
         ↓
   Detected: "Hey Assistant" (wake word)
         ↓
   Command: "what's the weather?"
         ↓
   Process and respond
   ```

3. **Without Wake Word:**
   ```
   User: "What's the weather?"
   Result: Ignored (no wake word)
   ```

### Configure Wake Word Behavior

**Disable wake word requirement:**
```env
VOICE_WAKE_WORD_REQUIRED=False
```

**Add custom wake words in .env:**
```env
VOICE_WAKE_WORDS=hey assistant,computer,jarvis,اے اسسٹنٹ
```

**Dynamically add wake word:**
```bash
curl -X POST http://localhost:8001/api/v1/voice/wake-word/add \
  -H "Content-Type: application/json" \
  -d '{"wake_word": "jarvis", "language": "en"}'
```

**Remove wake word:**
```bash
curl -X DELETE "http://localhost:8001/api/v1/voice/wake-word/jarvis"
```

---

## Troubleshooting

### Issue 1: "No microphone found"

**Problem:** API returns "No microphone available"

**Solutions:**

1. **Check microphone connection:**
   - Verify microphone is plugged in
   - Test with system audio settings
   - Try different USB port (for USB mics)

2. **Check permissions:**
   - macOS: System Preferences → Security & Privacy → Microphone
   - Linux: Check pulseaudio/alsa settings
   - Windows: Settings → Privacy → Microphone

3. **List audio devices:**
   ```python
   import pyaudio
   p = pyaudio.PyAudio()
   for i in range(p.get_device_count()):
       info = p.get_device_info_by_index(i)
       print(f"{i}: {info['name']} (inputs: {info['maxInputChannels']})")
   ```

4. **Set default device:**
   ```python
   # In voice_handler/speech_recognizer.py
   with sr.Microphone(device_index=1) as source:  # Use device 1
   ```

### Issue 2: PyAudio Installation Fails

**Problem:** `pip install pyaudio` fails with compilation errors

**Solutions:**

**Ubuntu/Debian:**
```bash
sudo apt-get install portaudio19-dev python3-pyaudio
pip install pyaudio
```

**macOS:**
```bash
brew install portaudio
pip install pyaudio
```

**Windows:**
1. Download pre-built wheel from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
2. Install: `pip install PyAudio-0.2.11-cp39-cp39-win_amd64.whl`

**Alternative - Use pipwin:**
```bash
pip install pipwin
pipwin install pyaudio
```

### Issue 3: Speech Not Recognized

**Problem:** API returns "Could not understand audio"

**Solutions:**

1. **Check microphone levels:**
   - Speak louder
   - Adjust system microphone volume
   - Move closer to microphone

2. **Re-calibrate:**
   ```bash
   curl -X POST http://localhost:8001/api/v1/voice/calibrate \
     -d '{"duration": 5}'
   ```

3. **Adjust energy threshold:**
   ```bash
   curl -X POST http://localhost:8001/api/v1/voice/listener/configure \
     -H "Content-Type: application/json" \
     -d '{"energy_threshold": 2000}'  # Lower = more sensitive
   ```

4. **Increase timeout:**
   ```bash
   curl -X POST http://localhost:8001/api/v1/voice/recognize \
     -d '{"timeout": 10, "phrase_time_limit": 15}'
   ```

5. **Check internet connection:**
   - Google Speech Recognition requires internet
   - Test with: `curl https://www.google.com`

### Issue 4: Text-to-Speech Not Working

**Problem:** No audio output when using `/voice/speak`

**Solutions:**

1. **Check speakers:**
   - Verify speakers/headphones connected
   - Check system volume
   - Test with other audio

2. **Install espeak (Linux):**
   ```bash
   sudo apt-get install espeak espeak-data
   ```

3. **Check pyttsx3 engine:**
   ```python
   import pyttsx3
   engine = pyttsx3.init()
   engine.say("test")
   engine.runAndWait()
   ```

4. **List available voices:**
   ```bash
   curl http://localhost:8001/api/v1/voice/settings
   ```

5. **Switch TTS engine (macOS):**
   - pyttsx3 uses `nsss` on macOS
   - Ensure voices installed: System Preferences → Accessibility → Spoken Content

### Issue 5: Wake Word Not Detected

**Problem:** Continuous listener doesn't respond to wake word

**Solutions:**

1. **Speak clearly:**
   - Say wake word distinctly
   - Pause after wake word before command
   - Example: "Hey Assistant [pause] create a task"

2. **Check wake word list:**
   ```bash
   curl http://localhost:8001/api/v1/voice/wake-words
   ```

3. **Lower sensitivity:**
   - Wake words must be detected in recognized text
   - Try louder/clearer pronunciation

4. **Disable wake word for testing:**
   ```bash
   curl -X POST http://localhost:8001/api/v1/voice/listener/configure \
     -H "Content-Type: application/json" \
     -d '{"wake_word_required": false}'
   ```

### Issue 6: High CPU Usage

**Problem:** Background listener uses too much CPU

**Solutions:**

1. **Increase check interval:**
   ```env
   VOICE_TIMEOUT=5  # Longer pause between checks
   ```

2. **Use single-command mode:**
   ```bash
   curl -X POST http://localhost:8001/api/v1/voice/listener/start \
     -d '{"continuous": false}'  # Single command then stop
   ```

3. **Disable auto-calibration:**
   ```env
   VOICE_AUTO_CALIBRATE=False
   ```

### Issue 7: Urdu Recognition Issues

**Problem:** Urdu speech not recognized correctly

**Solutions:**

1. **Verify language code:**
   ```bash
   curl -X POST http://localhost:8001/api/v1/voice/recognize \
     -d '{"language": "ur"}'  # Must be "ur" not "urdu"
   ```

2. **Google Speech API limitations:**
   - Urdu recognition may be less accurate
   - Speak slowly and clearly
   - Use common words

3. **Alternative - Use transliteration:**
   - Speak Urdu words in English script
   - Process with language detection

---

## Advanced Configuration

### Custom Speech Recognition Engine

By default, Google Speech Recognition is used. To use other engines:

**Edit `voice_handler/speech_recognizer.py`:**

```python
# Use Sphinx (offline)
text = self.recognizer.recognize_sphinx(audio, language=lang_code)

# Use Wit.ai
text = self.recognizer.recognize_wit(audio, key="WIT_AI_KEY")

# Use Microsoft Azure
text = self.recognizer.recognize_azure(audio, key="AZURE_KEY")
```

### Adjust Speech Rate and Volume

**Via environment:**
```env
VOICE_SPEECH_RATE=200  # Words per minute (default: 150)
VOICE_VOLUME=1.0       # 0.0 to 1.0 (default: 0.9)
```

**Via API:**
```bash
curl -X POST http://localhost:8001/api/v1/voice/speak \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Testing different rate and volume",
    "language": "en",
    "rate": 200,
    "volume": 1.0
  }'
```

### Background Listener Configuration

**Configure listener behavior:**
```bash
curl -X POST http://localhost:8001/api/v1/voice/listener/configure \
  -H "Content-Type: application/json" \
  -d '{
    "energy_threshold": 3000,
    "timeout": 5,
    "phrase_time_limit": 10,
    "wake_word_required": true
  }'
```

**Get current configuration:**
```bash
curl http://localhost:8001/api/v1/voice/settings
```

### Phrase Time Limit

Maximum seconds for a single command:

```env
VOICE_PHRASE_TIME_LIMIT=10  # Max 10 seconds per command
```

Longer phrases:
```bash
curl -X POST http://localhost:8001/api/v1/voice/recognize \
  -d '{"phrase_time_limit": 30}'  # 30 seconds max
```

### Energy Threshold

Microphone sensitivity (higher = less sensitive):

```env
VOICE_ENERGY_THRESHOLD=4000  # Default
```

**Quiet environment:** Lower threshold (2000-3000)
**Noisy environment:** Higher threshold (5000-8000)

Auto-calibration:
```env
VOICE_AUTO_CALIBRATE=True  # Adjusts automatically
```

---

## N8N Integration

### Voice-Triggered Workflows

**Example: Voice → N8N → Task Creation**

1. **Create N8N workflow:**
   - Trigger: Webhook
   - Action: Create task in AI Assistant

2. **Voice command invokes webhook:**
   ```bash
   # Say: "Create a task via N8N to review documents"
   curl -X POST http://localhost:8001/api/v1/voice/command \
     -d '{"language": "en"}'
   ```

3. **Assistant processes:**
   - Recognizes voice
   - Detects N8N intent
   - Sends to N8N webhook
   - Returns confirmation

### Voice Reminders from N8N

**Workflow: N8N → Voice Announcement**

```json
{
  "name": "Voice Reminder",
  "nodes": [
    {
      "name": "Schedule",
      "type": "n8n-nodes-base.scheduleTrigger",
      "parameters": {"rule": {"interval": [{"field": "cronExpression", "expression": "0 9 * * *"}]}}
    },
    {
      "name": "Speak Reminder",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "POST",
        "url": "http://localhost:8001/api/v1/voice/speak",
        "body": {"text": "Good morning! You have 5 pending tasks today.", "language": "en"}
      }
    }
  ]
}
```

---

## Security & Privacy

### Data Privacy

**Google Speech Recognition:**
- Audio sent to Google servers for processing
- Subject to Google's privacy policy
- Not suitable for sensitive information

**Alternatives for privacy:**
- Use Sphinx (offline, less accurate)
- Use local speech recognition models
- Disable voice features for sensitive tasks

### Authorized Voice Commands

**Limit voice commands to specific users:**

```python
# In api/voice.py
@router.post("/command")
async def voice_command(request: Request):
    # Add authentication
    api_key = request.headers.get("X-API-Key")
    if api_key not in AUTHORIZED_KEYS:
        raise HTTPException(401, "Unauthorized")
```

### Disable Voice Features

**Temporarily disable:**
```env
VOICE_ENABLED=False
```

**Per-session disable:**
```bash
curl -X POST http://localhost:8001/api/v1/voice/listener/stop
```

---

## Best Practices

1. **Calibrate regularly:**
   - Run calibration when environment changes
   - Different rooms have different noise levels

2. **Use clear speech:**
   - Speak naturally but clearly
   - Avoid background noise during commands

3. **Test both languages:**
   - Verify English and Urdu recognition
   - Adjust thresholds per language if needed

4. **Monitor CPU usage:**
   - Background listener uses resources
   - Stop when not in use

5. **Use wake words:**
   - Prevents accidental command execution
   - More reliable in continuous mode

6. **Handle errors gracefully:**
   - Check for recognition errors
   - Provide visual fallback (typing)

7. **Internet connection:**
   - Google Speech API requires internet
   - Have offline fallback (Sphinx)

---

## API Reference

### Core Endpoints

- `POST /api/v1/voice/recognize` - Speech-to-text
- `POST /api/v1/voice/speak` - Text-to-speech
- `POST /api/v1/voice/command` - Complete voice command
- `POST /api/v1/voice/listener/start` - Start background listener
- `POST /api/v1/voice/listener/stop` - Stop background listener
- `GET /api/v1/voice/listener/status` - Listener status
- `POST /api/v1/voice/calibrate` - Calibrate microphone
- `POST /api/v1/voice/test/microphone` - Test microphone
- `POST /api/v1/voice/test/tts` - Test TTS
- `GET /api/v1/voice/settings` - Get voice settings
- `GET /api/v1/voice/wake-words` - List wake words
- `POST /api/v1/voice/wake-word/add` - Add wake word
- `DELETE /api/v1/voice/wake-word/{word}` - Remove wake word

Full API documentation: http://localhost:8001/docs

---

## Support

### Resources

- [API Documentation](http://localhost:8001/docs)
- [Google Speech Recognition](https://cloud.google.com/speech-to-text)
- [pyttsx3 Documentation](https://pyttsx3.readthedocs.io/)
- [SpeechRecognition Library](https://github.com/Uberi/speech_recognition)

### Getting Help

1. Check logs for errors
2. Test microphone with system tools
3. Verify API responses
4. Review this guide's troubleshooting section
5. Test with simple commands first

---

## Next Steps

1. ✅ Complete installation and setup
2. ✅ Test microphone and calibrate
3. ✅ Try speech recognition in both languages
4. ✅ Configure wake words
5. ✅ Test background listener
6. ✅ Integrate with existing workflows
7. ✅ Set up N8N voice workflows

Happy automating with voice! 🎤🤖
