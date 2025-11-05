# Supabase PostgreSQL Setup Guide

Use Supabase's free managed PostgreSQL instead of local setup - much easier! ✨

---

## Why Supabase?

- ✅ **Free tier** - No credit card required
- ✅ **No installation** - Cloud-based PostgreSQL
- ✅ **Auto-backups** - Data is safe
- ✅ **Fast setup** - 2 minutes to get started
- ✅ **Works everywhere** - No local database needed

---

## Step-by-Step Setup (5 Minutes)

### Step 1: Create Supabase Account

1. Go to https://supabase.com
2. Click **"Start your project"**
3. Sign up with GitHub, Google, or email
4. Verify your email (if using email signup)

### Step 2: Create a New Project

1. Click **"New Project"**
2. Fill in the details:
   - **Name:** `veo-character-consistency` (or anything you like)
   - **Database Password:** Create a strong password (SAVE THIS!)
   - **Region:** Choose closest to you
   - **Pricing Plan:** Free

3. Click **"Create new project"**

⏳ Wait 1-2 minutes for project to initialize...

### Step 3: Get Database Connection String

Once your project is ready:

1. Click on **"Settings"** (gear icon) in sidebar
2. Click **"Database"**
3. Scroll down to **"Connection string"**
4. Select **"URI"** tab
5. Copy the connection string (looks like this):

```
postgresql://postgres:[YOUR-PASSWORD]@db.xxxxxxxxxxxxx.supabase.co:5432/postgres
```

6. **Replace `[YOUR-PASSWORD]`** with the password you created in Step 2

**Example:**
```
postgresql://postgres:MySecurePass123@db.abcdefghijk.supabase.co:5432/postgres
```

### Step 4: Configure Backend

1. Open `backend/.env` file
2. Update the `DATABASE_URL`:

```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.xxxxxxxxxxxxx.supabase.co:5432/postgres
GOOGLE_AI_API_KEY=your_google_ai_api_key_here
SECRET_KEY=change-this-to-random-secret
DEBUG=True
ALLOWED_ORIGINS=http://localhost:3000
```

3. Save the file

### Step 5: Start Backend

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
cd app
python main.py
```

The backend will automatically create all necessary tables in your Supabase database! 🎉

---

## Verify It's Working

### Check Tables in Supabase

1. Go to your Supabase dashboard
2. Click **"Table Editor"** in sidebar
3. You should see these tables:
   - `characters`
   - `character_face_references`
   - `character_outfits`
   - `projects`
   - `beats`
   - `shots`
   - `shot_versions`
   - `video_generations`

### Test the Connection

```bash
# Should return: {"status":"healthy"}
curl http://localhost:8000/health

# Test creating a character
curl -X POST http://localhost:8000/api/v1/characters \
  -H "Content-Type: application/json" \
  -d '{"name": "Test User", "age": 25}'
```

Check Supabase Table Editor - you should see the new character! ✅

---

## Connection String Formats

Supabase provides multiple formats. Use **URI** format:

### ✅ Correct Format (URI - Use This!)
```
postgresql://postgres:password@db.xxxxx.supabase.co:5432/postgres
```

### ❌ Don't Use These:
- **Session mode** - For short-lived connections
- **Transaction mode** - For serverless
- **JDBC** - For Java applications

---

## Supabase Dashboard Features

### View Your Data

**Table Editor:**
- See all characters, projects, shots
- Edit data directly
- Run SQL queries

**SQL Editor:**
```sql
-- View all characters
SELECT * FROM characters;

-- Count generations
SELECT COUNT(*) FROM video_generations;

-- Recent projects
SELECT * FROM projects ORDER BY created_at DESC LIMIT 10;
```

### Manage Database

**Settings → Database:**
- Connection pooling
- Database password
- API settings
- Extensions

---

## Security Best Practices

### 1. Database Password

**Strong password requirements:**
- At least 12 characters
- Mix of letters, numbers, symbols
- Don't reuse passwords

**Example good password:**
```
MyV3oApp#2025$Secure!
```

### 2. Connection String Security

**Never commit to Git:**
```bash
# .env is already in .gitignore
# NEVER commit .env file!
```

**For production, use environment variables:**
```bash
# On hosting platform (Vercel, Railway, etc.)
DATABASE_URL=postgresql://...your-supabase-url...
```

### 3. Row Level Security (Optional)

For production, enable RLS in Supabase:

1. Go to **Authentication** → **Policies**
2. Enable Row Level Security on tables
3. Create policies for access control

---

## Upgrading from Free Tier

**Free tier includes:**
- 500 MB database space
- 1 GB file storage
- 50,000 monthly active users
- Unlimited API requests

**When to upgrade:**
- Need more than 500 MB storage
- Want daily backups (vs weekly on free)
- Need more compute resources

**Pro tier ($25/month):**
- 8 GB database space
- 100 GB file storage
- Daily backups
- Point-in-time recovery

---

## Troubleshooting

### Issue: "Connection refused"

**Check:**
1. ✅ Password is correct in connection string
2. ✅ No spaces in connection string
3. ✅ Using URI format (not Session/Transaction mode)
4. ✅ Supabase project is active (not paused)

**Test connection:**
```bash
# Install psql if needed
brew install postgresql  # macOS
sudo apt install postgresql-client  # Ubuntu

# Test connection
psql "postgresql://postgres:PASSWORD@db.xxxxx.supabase.co:5432/postgres"

# If successful, you'll see:
# postgres=>

# Type \q to exit
```

### Issue: "Password authentication failed"

**Solution:**
1. Go to Supabase Dashboard
2. **Settings** → **Database**
3. Click **"Reset database password"**
4. Save new password
5. Update `backend/.env` with new password

### Issue: "Too many connections"

**Free tier limits:**
- Max 60 connections

**Solution:**
Add connection pooling to DATABASE_URL:
```env
DATABASE_URL=postgresql://postgres:PASSWORD@db.xxxxx.supabase.co:6543/postgres?pgbouncer=true
```

**Note:** Use port `6543` for pooling (instead of `5432`)

### Issue: "SSL required"

**Add SSL mode to connection string:**
```env
DATABASE_URL=postgresql://postgres:PASSWORD@db.xxxxx.supabase.co:5432/postgres?sslmode=require
```

### Issue: Tables not created

**Check backend logs:**
```bash
# Should see:
# INFO:     Application startup complete.
```

**Manually create tables:**
```bash
# In backend directory
python
>>> from app.core.database import Base, engine
>>> Base.metadata.create_all(bind=engine)
>>> exit()
```

---

## Migrating from Local PostgreSQL

If you already have data locally:

### Export Local Data

```bash
# Export from local database
pg_dump -U postgres video_ai_db > backup.sql
```

### Import to Supabase

```bash
# Import to Supabase (replace with your connection string)
psql "postgresql://postgres:PASSWORD@db.xxxxx.supabase.co:5432/postgres" < backup.sql
```

**Or use Supabase Dashboard:**
1. Go to **SQL Editor**
2. Paste SQL from backup.sql
3. Click **Run**

---

## Monitoring & Maintenance

### Database Usage

**Check in Supabase Dashboard:**
1. Go to **Settings** → **Billing**
2. See:
   - Database size
   - Bandwidth used
   - Storage used

### Performance

**Check query performance:**
1. Go to **Database** → **Roles**
2. Click on **postgres**
3. See slow queries

### Backups

**Free tier:**
- Weekly backups
- 7-day retention

**View backups:**
1. **Settings** → **Database**
2. Scroll to **Backups**
3. Download or restore

---

## Complete Setup Checklist

- [ ] Created Supabase account
- [ ] Created new project
- [ ] Saved database password
- [ ] Copied connection string (URI format)
- [ ] Updated `backend/.env` with DATABASE_URL
- [ ] Started backend server
- [ ] Verified tables created in Supabase
- [ ] Tested API connection
- [ ] Can see data in Table Editor

---

## Quick Reference

### Connection String Template
```
postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
```

### Where to Find:
- **Password:** You created this when setting up project
- **Project Ref:** Settings → General → Reference ID
- **Connection String:** Settings → Database → Connection string

### Important URLs
- **Dashboard:** https://app.supabase.com
- **Documentation:** https://supabase.com/docs
- **Status:** https://status.supabase.com

---

## Advantages of Supabase

✅ **No local installation** - Works immediately
✅ **Auto backups** - Data is safe
✅ **Accessible anywhere** - Cloud-based
✅ **Free tier** - No cost to start
✅ **Easy scaling** - Upgrade when needed
✅ **Real-time** - Built-in subscriptions
✅ **Dashboard** - Visual data management
✅ **Extensions** - pgvector, PostGIS, etc.

---

## Next Steps

Once Supabase is connected:

1. **Start backend:** `cd backend/app && python main.py`
2. **Start frontend:** `cd frontend && npm run dev`
3. **Open app:** http://localhost:3000
4. **Create characters** and upload face references
5. **Generate videos** with Veo 3.1

---

## Support

**Supabase Help:**
- Documentation: https://supabase.com/docs
- Discord: https://discord.supabase.com
- GitHub: https://github.com/supabase/supabase

**App Issues:**
- Check backend logs
- Verify connection string
- Test with curl commands

---

## Summary

**Instead of local PostgreSQL:**
1. ❌ No complex installation
2. ❌ No version issues
3. ❌ No port conflicts
4. ❌ No manual backups

**With Supabase:**
1. ✅ Sign up (2 minutes)
2. ✅ Copy connection string
3. ✅ Paste in `.env`
4. ✅ Done! 🎉

**Total setup time: 5 minutes vs 30+ minutes for local PostgreSQL!**
