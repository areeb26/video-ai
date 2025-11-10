# 🤖 AI Multitask Assistant - معاون AI

> **Bilingual AI Assistant for Multitasking and Automation**
>
> **کثیر کاموں اور خودکار عمل کے لیے دو لسانی AI معاون**

A powerful, local AI assistant that helps you automate tasks, manage files, execute system commands, and integrate with N8N workflows. Supports both English and Urdu languages.

ایک طاقتور، مقامی AI معاون جو آپ کو کاموں کو خودکار بنانے، فائلوں کو منظم کرنے، سسٹم کمانڈز چلانے اور N8N ورک فلوز کے ساتھ مربوط کرنے میں مدد کرتا ہے۔ انگریزی اور اردو دونوں زبانوں کو سپورٹ کرتا ہے۔

---

## 📖 Documentation | دستاویزات

- [English Documentation](docs/README_EN.md)
- [اردو دستاویزات](docs/README_UR.md)

---

## ✨ Features | خصوصیات

### English
- **🌐 Bilingual Support**: Communicate in English or Urdu
- **📝 Task Management**: Create, track, and manage tasks with reminders
- **📁 File Operations**: Safe file creation, reading, editing, and organization
- **⚡ N8N Integration**: Connect with N8N for powerful workflow automation
- **💻 System Commands**: Execute safe system commands with security checks
- **🔒 Security First**: Built-in safety checks for all operations
- **🎯 Natural Language**: Interact using natural language commands
- **🗄️ Local Database**: All data stored locally on your machine

### اردو
- **🌐 دو لسانی سپورٹ**: انگریزی یا اردو میں بات چیت کریں
- **📝 کام کا انتظام**: یاد دہانیوں کے ساتھ کام بنائیں، ٹریک کریں اور منظم کریں
- **📁 فائل آپریشنز**: محفوظ فائل بنانا، پڑھنا، ترمیم کرنا اور ترتیب دینا
- **⚡ N8N انضمام**: طاقتور ورک فلو آٹومیشن کے لیے N8N سے جڑیں
- **💻 سسٹم کمانڈز**: حفاظتی جانچوں کے ساتھ محفوظ سسٹم کمانڈز چلائیں
- **🔒 سیکیورٹی اول**: تمام کاموں کے لیے بلٹ ان حفاظتی جانچیں
- **🎯 قدرتی زبان**: قدرتی زبان کے احکام استعمال کرتے ہوئے تعامل کریں
- **🗄️ مقامی ڈیٹا بیس**: تمام ڈیٹا آپ کی مشین پر مقامی طور پر محفوظ ہے

---

## 🚀 Quick Start | فوری شروعات

### Prerequisites | پیشگی تقاضے

```bash
# Python 3.10 or higher
python --version

# N8N (optional but recommended)
# Install with: npm install -g n8n
```

### Installation | تنصیب

```bash
# 1. Navigate to the ai-assistant directory
cd ai-assistant

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy and configure environment
cp .env.example .env
# Edit .env with your settings

# 5. Run the assistant
python main.py
```

The assistant will be available at: `http://localhost:8001`

---

## 💬 Usage Examples | استعمال کی مثالیں

### English Commands

```bash
# Create a task
"Create a task to buy groceries tomorrow"
"Add a high priority task: Review code"
"Remind me to call John at 3pm"

# Manage tasks
"List my tasks"
"Show pending tasks"
"Complete task buy groceries"

# File operations
"Create a file called notes.txt"
"Read file notes.txt"
"Edit file notes.txt and add 'Meeting notes'"

# System commands
"Run command ls"
"Execute pwd"

# N8N workflows
"Trigger workflow send-email"
"Run n8n workflow task-automation"
```

### اردو کمانڈز

```bash
# کام بنائیں
"کل گروسری خریدنے کا کام بنائیں"
"اہم ترجیح کا کام: کوڈ کا جائزہ لیں"
"مجھے 3 بجے جان کو کال کرنے کی یاد دلائیں"

# کام منظم کریں
"میرے کام دکھائیں"
"زیر التوا کام دکھائیں"
"گروسری خریدنے کا کام مکمل کریں"

# فائل آپریشنز
"notes.txt نام کی فائل بنائیں"
"notes.txt فائل پڑھیں"
"notes.txt فائل ایڈٹ کریں اور 'میٹنگ نوٹس' شامل کریں"

# سسٹم کمانڈز
"ls کمانڈ چلائیں"
"pwd رن کریں"

# N8N ورک فلوز
"send-email ورک فلو چلائیں"
"task-automation n8n چلائیں"
```

---

## 🏗️ Architecture | فن تعمیر

```
ai-assistant/
├── api/              # FastAPI endpoints
├── core/             # Configuration and database
├── models/           # Database models
├── schemas/          # Pydantic schemas
├── services/         # Business logic
│   ├── task_manager.py
│   ├── file_operations.py
│   ├── n8n_integration.py
│   └── system_commands.py
├── modules/          # Core modules
│   └── nlp_processor.py  # Bilingual NLP
├── templates/        # Web interface
├── n8n_workflows/    # Example N8N workflows
├── docs/             # Documentation
└── main.py           # Application entry point
```

---

## 🔌 API Endpoints

### Main Assistant
- `POST /api/v1/assistant` - Natural language interface

### Tasks
- `GET /api/v1/tasks` - List all tasks
- `POST /api/v1/tasks` - Create a task
- `GET /api/v1/tasks/{id}` - Get task details
- `PUT /api/v1/tasks/{id}` - Update task
- `DELETE /api/v1/tasks/{id}` - Delete task
- `POST /api/v1/tasks/{id}/complete` - Complete task

### Files
- `POST /api/v1/files/create` - Create file
- `POST /api/v1/files/read` - Read file
- `POST /api/v1/files/edit` - Edit file
- `GET /api/v1/files/list` - List files

### N8N Workflows
- `POST /api/v1/n8n/trigger` - Trigger webhook
- `POST /api/v1/n8n/execute/{id}` - Execute workflow
- `GET /api/v1/n8n/workflows` - List workflows

Full API documentation: `http://localhost:8001/docs`

---

## 🔧 Configuration | ترتیب

Edit `.env` file:

```env
# Application
PORT=8001
DEBUG=True

# N8N Integration
N8N_WEBHOOK_URL=http://localhost:5678/webhook
N8N_API_KEY=your-api-key

# Language
DEFAULT_LANGUAGE=en  # or ur

# Workspace
WORKSPACE_DIR=/path/to/your/workspace
```

---

## 🛡️ Security | سیکیورٹی

The assistant includes multiple safety layers:

- **File Operations**: Restricted to workspace directory
- **System Commands**: Whitelist-based command execution
- **Path Traversal**: Protection against malicious paths
- **File Size Limits**: Prevents resource exhaustion
- **Command Blocking**: Dangerous commands are blocked

معاون میں کئی حفاظتی تہیں شامل ہیں:

- **فائل آپریشنز**: ورک اسپیس ڈائریکٹری تک محدود
- **سسٹم کمانڈز**: وائٹ لسٹ پر مبنی کمانڈ عمل
- **راستہ عبور**: بدنیتی راستوں کے خلاف تحفظ
- **فائل سائز حدود**: وسائل کی کمی سے بچاتا ہے
- **کمانڈ بلاکنگ**: خطرناک کمانڈز بلاک ہیں

---

## 🤝 Contributing | تعاون

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

تعاون کا خیرمقدم ہے! تفصیلات کے لیے [CONTRIBUTING.md](CONTRIBUTING.md) دیکھیں۔

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

---

## 🙏 Support | معاونت

- 📖 [Documentation](docs/)
- 🐛 [Report Issues](https://github.com/yourusername/ai-assistant/issues)
- 💬 [Discussions](https://github.com/yourusername/ai-assistant/discussions)

---

Made with ❤️ for automation enthusiasts
خودکاری کے شوقین افراد کے لیے ❤️ کے ساتھ بنایا گیا
