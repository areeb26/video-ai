# Quick Start Guide

Get up and running with AI Multitask Assistant in 5 minutes!

## Installation

### Option 1: Automated Setup (Linux/Mac)

```bash
cd ai-assistant
./setup.sh
```

### Option 2: Automated Setup (Windows/Cross-platform)

```bash
cd ai-assistant
python setup.py
```

### Option 3: Manual Setup

```bash
cd ai-assistant

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
```

## Quick Configuration

Edit `.env` file and set at minimum:

```env
# Required
WORKSPACE_DIR=/path/to/your/workspace

# Optional (for N8N)
N8N_WEBHOOK_URL=http://localhost:5678/webhook
```

## Start the Assistant

### Using start script (Linux/Mac)

```bash
./start.sh
```

### Manual start

```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
python main.py
```

## Access

- **Web Interface**: http://localhost:8001
- **API Docs**: http://localhost:8001/docs

## First Commands

Try these commands in the web interface:

### English
```
Create a task to test the assistant
List my tasks
Create a file called test.txt
```

### Urdu
```
ٹیسٹ کا کام بنائیں
میرے کام دکھائیں
test.txt نام کی فائل بنائیں
```

## Next Steps

1. **Read the full documentation**: [docs/README_EN.md](docs/README_EN.md) or [docs/README_UR.md](docs/README_UR.md)
2. **Setup N8N** (optional): Install with `npm install -g n8n`
3. **Import workflows**: See [n8n_workflows/README.md](n8n_workflows/README.md)
4. **Customize**: Edit `.env` for your preferences

## Troubleshooting

**Port already in use?**
```bash
# Change PORT in .env file
PORT=8002
```

**Dependencies error?**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Can't access web interface?**
- Check if server is running
- Try http://127.0.0.1:8001 instead
- Check firewall settings

## Support

- [English Documentation](docs/README_EN.md)
- [اردو دستاویزات](docs/README_UR.md)
- [GitHub Issues](https://github.com/yourusername/ai-assistant/issues)

Happy automating! 🚀
