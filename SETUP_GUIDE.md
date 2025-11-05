# Local Setup Guide

Quick guide to run the Veo Character Consistency App on your local machine.

---

## Prerequisites

Before you start, make sure you have:

- ✅ **Python 3.10+** installed
- ✅ **Node.js 18+** and npm installed
- ✅ **PostgreSQL 14+** installed and running
- ✅ **Google AI API Key** with Veo 3.1 access

---

## Quick Start (5 Steps)

### Step 1: Install PostgreSQL

**On macOS:**
```bash
brew install postgresql@14
brew services start postgresql@14
createdb video_ai_db
```

**On Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo -u postgres createdb video_ai_db
```

**On Windows:**
Download and install from: https://www.postgresql.org/download/windows/

Then create database:
```bash
createdb video_ai_db
```

### Step 2: Setup Backend

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies (this takes 5-10 minutes due to ML libraries)
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env and add your Google AI API key
nano .env  # or use any text editor
```

**Edit `.env` file:**
```env
DATABASE_URL=postgresql://YOUR_USERNAME:YOUR_PASSWORD@localhost:5432/video_ai_db
GOOGLE_AI_API_KEY=your_google_ai_api_key_here
SECRET_KEY=change-this-to-a-random-secret-key
DEBUG=True
ALLOWED_ORIGINS=http://localhost:3000
```

**Replace:**
- `YOUR_USERNAME` - your PostgreSQL username (usually your system username or `postgres`)
- `YOUR_PASSWORD` - your PostgreSQL password (leave empty if no password)
- `your_google_ai_api_key_here` - your actual Google AI API key

**Start the backend:**
```bash
cd app
python main.py
```

You should see:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

✅ **Backend is running!** Visit http://localhost:8000/api/v1/docs to see the API documentation.

### Step 3: Setup Frontend (New Terminal)

```bash
# Open a new terminal window
cd frontend

# Install dependencies (takes 2-5 minutes)
npm install

# Create .env.local file
cp .env.local.example .env.local

# Start the frontend
npm run dev
```

You should see:
```
  ▲ Next.js 14.1.0
  - Local:        http://localhost:3000
  - Ready in 2.5s
```

✅ **Frontend is running!** Visit http://localhost:3000

### Step 4: Verify Everything Works

Open your browser and go to:
- **Frontend:** http://localhost:3000
- **Backend API Docs:** http://localhost:8000/api/v1/docs
- **Backend Health:** http://localhost:8000/health

You should see:
- ✅ Beautiful teal-themed homepage
- ✅ Navigation working
- ✅ API documentation accessible

### Step 5: Test the API

```bash
# Test if backend is responding
curl http://localhost:8000/health

# Should return: {"status":"healthy"}
```

---

## Complete Setup (Detailed)

### PostgreSQL Configuration

If you need to configure PostgreSQL:

**Find your PostgreSQL username:**
```bash
whoami  # This is usually your username
```

**Set PostgreSQL password (if needed):**
```bash
# On macOS/Linux:
sudo -u postgres psql

# In PostgreSQL prompt:
ALTER USER postgres WITH PASSWORD 'your_password';
\q
```

**Test database connection:**
```bash
psql -U YOUR_USERNAME -d video_ai_db

# If successful, you'll see:
# video_ai_db=#

# Type \q to exit
```

### Environment Variables Explained

**Backend `.env`:**
```env
# Database connection
# Format: postgresql://username:password@host:port/database_name
DATABASE_URL=postgresql://postgres:@localhost:5432/video_ai_db

# Your Google AI API key (required for video generation)
GOOGLE_AI_API_KEY=AIzaSy...your_key_here

# Secret key for security (change this!)
SECRET_KEY=some-random-secret-key-123

# Debug mode (set to False in production)
DEBUG=True

# Allow requests from frontend
ALLOWED_ORIGINS=http://localhost:3000

# File upload directories (created automatically)
UPLOAD_DIR=./uploads
MEDIA_DIR=./media

# Video generation settings
DEFAULT_VIDEO_QUALITY=low
MAX_FACE_EMBEDDINGS=10
MIN_FACE_EMBEDDINGS=3
```

**Frontend `.env.local`:**
```env
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

---

## Troubleshooting

### Backend Issues

**Issue: `psycopg2` installation fails**
```bash
# Install PostgreSQL dev package
# On Ubuntu/Debian:
sudo apt-get install libpq-dev python3-dev

# On macOS:
brew install postgresql
```

**Issue: `ModuleNotFoundError: No module named 'cv2'`**
```bash
# Install system dependencies for OpenCV
# On Ubuntu/Debian:
sudo apt-get install libgl1 libglib2.0-0

# Then reinstall opencv
pip install opencv-python-headless --force-reinstall
```

**Issue: Database connection error**
```bash
# Check if PostgreSQL is running
# On macOS:
brew services list | grep postgresql

# On Ubuntu/Linux:
sudo systemctl status postgresql

# Test connection
psql -U postgres -d video_ai_db
```

**Issue: Port 8000 already in use**
```bash
# Find what's using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use a different port in main.py:
# uvicorn.run(app, host="0.0.0.0", port=8001)
```

### Frontend Issues

**Issue: Port 3000 already in use**
```bash
# Find what's using port 3000
lsof -i :3000

# Kill the process
kill -9 <PID>

# Or change port:
npm run dev -- -p 3001
```

**Issue: API connection error**

Check that:
1. Backend is running on port 8000
2. `.env.local` has correct API URL
3. CORS is configured in backend

**Issue: Module not found errors**
```bash
# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Database Issues

**Issue: Database doesn't exist**
```bash
# Create it
createdb video_ai_db

# Or using psql:
psql -U postgres
CREATE DATABASE video_ai_db;
\q
```

**Issue: Permission denied**
```bash
# Grant permissions
sudo -u postgres psql

GRANT ALL PRIVILEGES ON DATABASE video_ai_db TO your_username;
\q
```

**Issue: Tables don't exist**

The app creates tables automatically on first run. If there are issues:
```bash
# Check logs in the backend terminal
# Tables are created in app/main.py:
# Base.metadata.create_all(bind=engine)
```

---

## Getting Your Google AI API Key

1. Go to https://ai.google.dev/
2. Sign in with your Google account
3. Click "Get API Key"
4. Create a new project or select existing
5. Enable "Generative Language API"
6. Copy your API key
7. Add to backend `.env` file

**Note:** Veo 3.1 requires special access. If you don't have access yet:
- The app will still run
- Character and project features work
- Video generation will fail (expected)
- Request access at https://labs.google/veo

---

## Running in Production

For production deployment:

1. **Set environment variables:**
```env
DEBUG=False
SECRET_KEY=<strong-random-key>
DATABASE_URL=<production-database-url>
ALLOWED_ORIGINS=https://yourdomain.com
```

2. **Use a production database:**
   - PostgreSQL on AWS RDS, Google Cloud SQL, or similar

3. **Use a process manager:**
```bash
# Install gunicorn
pip install gunicorn

# Run backend
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

4. **Build frontend for production:**
```bash
cd frontend
npm run build
npm start
```

5. **Use a reverse proxy:**
   - Nginx or Apache
   - Configure SSL certificates
   - Set up load balancing

---

## Development Tips

### Hot Reload

Both backend and frontend support hot reload:
- **Backend:** Uvicorn auto-reloads on file changes
- **Frontend:** Next.js auto-reloads on save

### API Testing

Use the interactive API docs:
http://localhost:8000/api/v1/docs

Or use curl:
```bash
# Test character creation
curl -X POST http://localhost:8000/api/v1/characters \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Character", "age": 25}'
```

### Database Management

View database tables:
```bash
psql -U postgres -d video_ai_db

# List tables
\dt

# View table structure
\d characters

# Query data
SELECT * FROM characters;

# Exit
\q
```

### Logs

**Backend logs:** Shown in terminal where you ran `python main.py`

**Frontend logs:**
- Terminal: Build logs
- Browser console: Runtime logs

---

## Next Steps

Once running:

1. **Create a character:**
   - Go to http://localhost:3000/characters
   - Click "New Character"
   - Fill in details

2. **Upload face references:**
   - Open a character
   - Upload 3-10 face images

3. **Create a project:**
   - Go to http://localhost:3000/projects
   - Create a new project
   - Add beats and shots

4. **Generate a video:**
   - Go to http://localhost:3000/generation
   - Enter a prompt
   - Select character (optional)
   - Click "Generate Video"

---

## Support

**Issues?**
- Check the troubleshooting section above
- Review logs in both terminals
- Check PostgreSQL is running
- Verify API key is correct

**Need help?**
- GitHub Issues: [your-repo/issues]
- Email: support@example.com

---

## Summary Checklist

- [ ] PostgreSQL installed and running
- [ ] Database `video_ai_db` created
- [ ] Backend dependencies installed
- [ ] Backend `.env` configured with API key
- [ ] Backend running on http://localhost:8000
- [ ] Frontend dependencies installed
- [ ] Frontend `.env.local` configured
- [ ] Frontend running on http://localhost:3000
- [ ] Can access homepage
- [ ] Can access API docs

Once all checkboxes are ✅, you're ready to go! 🚀
