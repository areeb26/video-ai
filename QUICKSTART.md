# ⚡ Quick Start - Get Running in 5 Minutes

The fastest way to run the Veo Character Consistency App.

---

## Prerequisites

Install these first:
- **Python 3.10+** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** - [Download](https://nodejs.org/)

---

## Step 1: Get Your Credentials (2 minutes)

### A. Supabase Database (Free)

1. Go to **https://supabase.com** → Sign up
2. Create new project → Save password
3. Go to **Settings** → **Database** → Copy **Connection string (URI)**

Example: `postgresql://postgres:password@db.xxxxx.supabase.co:5432/postgres`

### B. Google AI API Key

1. Go to **https://aistudio.google.com/app/apikey**
2. Sign in with Google
3. Click **"Create API key"** → Copy it

Example: `AIzaSyC1234567890abcdefg`

---

## Step 2: Configure Backend (1 minute)

```bash
cd backend

# Copy example file
cp .env.example .env

# Edit .env and add your credentials
nano .env   # or use any text editor
```

**In `.env`, replace these:**
```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.xxxxx.supabase.co:5432/postgres
GOOGLE_AI_API_KEY=AIzaSyC1234567890abcdefg
```

Save and close.

---

## Step 3: Run the App (1 command!)

### Option A: Run Everything (Easiest)

```bash
chmod +x start.sh
./start.sh
```

This starts both backend and frontend automatically! 🎉

### Option B: Run Separately

**Terminal 1 - Backend:**
```bash
cd backend
chmod +x start.sh
./start.sh
```

**Terminal 2 - Frontend:**
```bash
cd frontend
chmod +x start.sh
./start.sh
```

---

## Step 4: Open in Browser

**Frontend (Main App):**
```
http://localhost:3000
```

**API Documentation:**
```
http://localhost:8000/api/v1/docs
```

---

## ✅ That's It!

You should see:
- ✨ Beautiful teal-themed homepage
- 🎯 Characters, Projects, Generate pages
- 📖 Interactive API docs

---

## 🎬 Quick Usage

### Create a Character
1. Go to **http://localhost:3000/characters**
2. Click **"New Character"**
3. Fill in name, age, physical traits
4. Upload 3-10 face photos

### Generate a Video
1. Go to **http://localhost:3000/generation**
2. Type a prompt: "A person walking in a park"
3. Select character (optional)
4. Click **"Generate Video"**

---

## 🆘 Troubleshooting

### Backend won't start?

**Check logs:**
```bash
tail -f backend.log
```

**Common fixes:**
- Verify `.env` has correct credentials
- No extra spaces or quotes in `.env`
- Supabase connection string is correct

### Frontend won't start?

**Check logs:**
```bash
tail -f frontend.log
```

**Common fixes:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Port already in use?

**Kill existing process:**
```bash
# Backend (port 8000)
lsof -i :8000
kill -9 <PID>

# Frontend (port 3000)
lsof -i :3000
kill -9 <PID>
```

---

## 📖 Full Documentation

For detailed setup:
- **SUPABASE_SETUP.md** - Database setup guide
- **GOOGLE_ULTRA_SETUP.md** - API key guide
- **SETUP_GUIDE.md** - Complete manual setup
- **API_DOCUMENTATION.md** - API reference

---

## 🔥 Next Steps

1. **Create characters** with face references
2. **Build projects** with story timelines
3. **Generate videos** with Veo 3.1
4. **Use the API** programmatically

Check **API_DOCUMENTATION.md** for curl/Python/JavaScript examples!

---

## 🎉 You're Ready!

Start creating videos with perfect character consistency! 🚀
