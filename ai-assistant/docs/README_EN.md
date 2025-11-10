# AI Multitask Assistant - English Documentation

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Usage Guide](#usage-guide)
5. [API Reference](#api-reference)
6. [N8N Integration](#n8n-integration)
7. [Troubleshooting](#troubleshooting)

---

## Introduction

The AI Multitask Assistant is a Python-based local server application that helps you automate daily tasks, manage files, execute system commands, and integrate with N8N workflows. It features:

- **Natural Language Processing**: Understand commands in English and Urdu
- **Task Management**: Create, track, and complete tasks with reminders
- **File Operations**: Safe file manipulation within a workspace
- **System Commands**: Execute whitelisted system commands securely
- **N8N Integration**: Trigger workflows and automate complex processes
- **Web Interface**: Simple web UI for interaction
- **REST API**: Full API for programmatic access

---

## Installation

### Step 1: Prerequisites

Ensure you have:
- Python 3.10 or higher
- pip (Python package manager)
- (Optional) N8N installed for workflow automation

### Step 2: Install the Assistant

```bash
# Navigate to the ai-assistant directory
cd ai-assistant

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your settings
nano .env  # or use your preferred editor
```

Key settings to configure:
- `WORKSPACE_DIR`: Directory for file operations
- `N8N_WEBHOOK_URL`: Your N8N webhook base URL
- `N8N_API_KEY`: Your N8N API key (if using API)
- `DEFAULT_LANGUAGE`: Default language (en or ur)

### Step 4: Run the Assistant

```bash
python main.py
```

The assistant will start on `http://localhost:8001`

---

## Configuration

### Environment Variables

Edit `.env` file to customize:

#### Application Settings
- `APP_NAME`: Application name
- `PORT`: Server port (default: 8001)
- `DEBUG`: Debug mode (True/False)

#### Security
- `SECRET_KEY`: Secret key for security (change in production)
- `ALLOWED_ORIGINS`: CORS allowed origins

#### Database
- `DATABASE_PATH`: SQLite database path

#### N8N Integration
- `N8N_WEBHOOK_URL`: N8N webhook URL
- `N8N_API_URL`: N8N API URL
- `N8N_API_KEY`: Your N8N API key

#### Language
- `DEFAULT_LANGUAGE`: Default language (en or ur)
- `SUPPORTED_LANGUAGES`: Comma-separated list of supported languages

#### File Operations
- `WORKSPACE_DIR`: Safe workspace directory
- `MAX_FILE_SIZE`: Maximum file size in bytes
- `ALLOWED_FILE_EXTENSIONS`: Comma-separated allowed extensions

#### System Commands
- `ENABLE_SYSTEM_COMMANDS`: Enable/disable command execution
- `SAFE_COMMANDS`: Comma-separated safe commands
- `BLOCKED_COMMANDS`: Comma-separated blocked patterns

---

## Usage Guide

### Using the Web Interface

1. Open your browser to `http://localhost:8001`
2. Select your language (English or Urdu)
3. Type commands in the input box
4. Press Enter or click Send

### Using the API

#### Create a Task

```bash
curl -X POST http://localhost:8001/api/v1/assistant \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Create a task to buy groceries tomorrow",
    "language": "en"
  }'
```

#### List Tasks

```bash
curl http://localhost:8001/api/v1/tasks
```

#### File Operations

```bash
# Create a file
curl -X POST http://localhost:8001/api/v1/files/create \
  -H "Content-Type: application/json" \
  -d '{
    "operation_type": "create",
    "file_path": "notes.txt",
    "content": "My notes here",
    "language": "en"
  }'

# Read a file
curl -X POST http://localhost:8001/api/v1/files/read \
  -H "Content-Type: application/json" \
  -d '{
    "operation_type": "read",
    "file_path": "notes.txt"
  }'
```

### Natural Language Commands

The assistant understands various natural language patterns:

#### Task Commands
- "Create a task to [description]"
- "Add a task: [description]"
- "Remind me to [description]"
- "List my tasks"
- "Show pending tasks"
- "Complete task [id or name]"

#### File Commands
- "Create a file called [filename]"
- "Read file [filename]"
- "Edit file [filename]"
- "Show me file [filename]"

#### System Commands
- "Run command [command]"
- "Execute [command]"

#### N8N Commands
- "Trigger workflow [workflow-name]"
- "Run n8n workflow [workflow-name]"

---

## API Reference

### Assistant Endpoint

**POST** `/api/v1/assistant`

Process natural language commands.

Request:
```json
{
  "message": "Create a task to review code",
  "language": "en"
}
```

Response:
```json
{
  "message": "Task created successfully!",
  "language": "en",
  "intent": "create_task",
  "entities": {},
  "actions": [
    {
      "action": "task_created",
      "task_id": 1,
      "title": "review code"
    }
  ],
  "success": true
}
```

### Task Endpoints

**GET** `/api/v1/tasks` - List all tasks
**POST** `/api/v1/tasks` - Create a task
**GET** `/api/v1/tasks/{id}` - Get task by ID
**PUT** `/api/v1/tasks/{id}` - Update task
**DELETE** `/api/v1/tasks/{id}` - Delete task
**POST** `/api/v1/tasks/{id}/complete` - Mark task as complete

### File Endpoints

**POST** `/api/v1/files/create` - Create file
**POST** `/api/v1/files/read` - Read file
**POST** `/api/v1/files/edit` - Edit file
**POST** `/api/v1/files/delete` - Delete file
**POST** `/api/v1/files/move` - Move file
**POST** `/api/v1/files/copy` - Copy file
**GET** `/api/v1/files/list` - List files

### N8N Endpoints

**POST** `/api/v1/n8n/trigger` - Trigger webhook
**POST** `/api/v1/n8n/execute/{workflow_id}` - Execute workflow
**GET** `/api/v1/n8n/status/{execution_id}` - Get execution status
**GET** `/api/v1/n8n/workflows` - List all workflows

Full interactive API documentation available at: `http://localhost:8001/docs`

---

## N8N Integration

### Setting Up N8N

1. Install N8N:
```bash
npm install -g n8n
```

2. Start N8N:
```bash
n8n start
```

3. Access N8N at `http://localhost:5678`

### Importing Workflows

1. Navigate to the `n8n_workflows` directory
2. Open N8N web interface
3. Click **Import from File**
4. Select a workflow JSON file
5. Activate the workflow

### Example Workflows

#### Task Automation
Triggers when tasks are created and sends notifications for urgent tasks.

Webhook: `http://localhost:5678/webhook/task-created`

#### Email Automation
Sends emails based on natural language commands.

Webhook: `http://localhost:5678/webhook/send-email`

### Creating Custom Workflows

You can create custom workflows for:
- Calendar integration
- Slack/Teams notifications
- Database synchronization
- Web scraping
- Report generation
- And more!

---

## Troubleshooting

### Assistant Won't Start

**Problem**: Server fails to start

**Solutions**:
1. Check if port 8001 is available
2. Verify virtual environment is activated
3. Ensure all dependencies are installed: `pip install -r requirements.txt`
4. Check for errors in the console output

### Tasks Not Creating

**Problem**: Task creation commands don't work

**Solutions**:
1. Check database exists: Verify `DATABASE_PATH` in .env
2. Check database permissions
3. Try restarting the assistant
4. Check API logs for errors

### File Operations Failing

**Problem**: Can't create or read files

**Solutions**:
1. Verify `WORKSPACE_DIR` exists and is writable
2. Check file permissions
3. Ensure file path doesn't contain `..` (path traversal)
4. Verify file extension is in `ALLOWED_FILE_EXTENSIONS`

### N8N Integration Not Working

**Problem**: Webhooks not triggering

**Solutions**:
1. Verify N8N is running: `http://localhost:5678`
2. Check `N8N_WEBHOOK_URL` in .env
3. Ensure workflow is activated in N8N
4. Test webhook directly with curl:
```bash
curl -X POST http://localhost:5678/webhook/your-workflow \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

### System Commands Blocked

**Problem**: Commands won't execute

**Solutions**:
1. Check if `ENABLE_SYSTEM_COMMANDS=True` in .env
2. Verify command is in `SAFE_COMMANDS` list
3. Ensure command doesn't match `BLOCKED_COMMANDS` patterns
4. Try adding command to safe list

### Language Detection Issues

**Problem**: Wrong language detected

**Solutions**:
1. Explicitly specify language in API request
2. Use more language-specific words
3. Set `DEFAULT_LANGUAGE` in .env

---

## Best Practices

1. **Security**:
   - Keep `SECRET_KEY` secure and unique
   - Only whitelist necessary system commands
   - Regularly review `ALLOWED_FILE_EXTENSIONS`
   - Don't expose the API to the internet without authentication

2. **Performance**:
   - Keep workspace directory organized
   - Regularly clean up completed tasks
   - Monitor database size

3. **N8N Integration**:
   - Test workflows thoroughly before activation
   - Use error handling in workflows
   - Monitor workflow execution logs

4. **Backup**:
   - Regularly backup the SQLite database
   - Keep copies of important files
   - Export N8N workflows periodically

---

## Support

For more help:
- Check the [main README](../README.md)
- Review API documentation at `/docs`
- Check N8N workflows in `n8n_workflows/`
- Open an issue on GitHub
