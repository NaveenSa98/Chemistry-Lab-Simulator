# Deploying Chemistry Lab Simulator to Render (Free)

This guide will walk you through deploying your Chemistry Lab Simulator to Render's free tier.

## Prerequisites

1. A GitHub account
2. A Render account (sign up at https://render.com)
3. Google API Key for AI features (get from https://makersuite.google.com/app/apikey)

## Step 1: Prepare Your Repository

### 1.1 Initialize Git Repository (if not already done)

```bash
git init
git add .
git commit -m "Initial commit - Chemistry Lab Simulator"
```

### 1.2 Create a GitHub Repository

1. Go to https://github.com/new
2. Create a new repository named `chemistry-lab-simulator`
3. Do NOT initialize with README (we already have code)
4. Click "Create repository"

### 1.3 Push Your Code to GitHub

```bash
git remote add origin https://github.com/YOUR_USERNAME/chemistry-lab-simulator.git
git branch -M main
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username.

## Step 2: Deploy to Render

### 2.1 Sign Up/Login to Render

1. Go to https://render.com
2. Click "Get Started" or "Sign In"
3. Sign up with your GitHub account (recommended)

### 2.2 Create a PostgreSQL Database

1. From your Render Dashboard, click "New +"
2. Select "PostgreSQL"
3. Configure the database:
   - **Name**: `chemlab-db`
   - **Database**: `chemlab`
   - **User**: `chemlab_user` (or leave default)
   - **Region**: Choose closest to your location
   - **Plan**: Select **Free**
4. Click "Create Database"
5. **IMPORTANT**: Save the connection details (especially the Internal Database URL)

### 2.3 Create the Web Service

1. From your Render Dashboard, click "New +"
2. Select "Web Service"
3. Connect your GitHub repository:
   - Click "Connect" next to your `chemistry-lab-simulator` repository
   - If you don't see it, click "Configure account" to grant access

4. Configure the web service:

   **Basic Settings:**
   - **Name**: `chemistry-lab-simulator`
   - **Region**: Same as your database
   - **Branch**: `main`
   - **Root Directory**: Leave blank
   - **Runtime**: `Python 3`

   **Build & Deploy:**
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT backend.app:app`

   **Plan:**
   - Select **Free**

5. Click "Advanced" to add environment variables

## Step 3: Configure Environment Variables

In the "Environment Variables" section, add the following:

### 3.1 Add Database Connection

1. Click "Add Environment Variable"
2. **Key**: `DATABASE_URL`
3. **Value**: Copy the "Internal Database URL" from your PostgreSQL database
   - Go to your database page
   - Copy the "Internal Database URL" (starts with `postgresql://`)
   - Paste it here

### 3.2 Add Google API Key

1. Click "Add Environment Variable"
2. **Key**: `GOOGLE_API_KEY`
3. **Value**: Your Google API key from https://makersuite.google.com/app/apikey

### 3.3 Add Python Version (Optional but Recommended)

1. Click "Add Environment Variable"
2. **Key**: `PYTHON_VERSION`
3. **Value**: `3.11.0`

### 3.4 Add Additional Database Variables (Optional)

These are auto-parsed from DATABASE_URL, but you can add them explicitly:

- `DB_HOST`: (extracted from DATABASE_URL)
- `DB_PORT`: `5432`
- `DB_NAME`: `chemlab`
- `DB_USER`: (your database user)
- `DB_PASSWORD`: (your database password)

## Step 4: Deploy!

1. Click "Create Web Service"
2. Render will now:
   - Clone your repository
   - Install dependencies
   - Start your application
3. Wait for the build to complete (2-5 minutes)

## Step 5: Verify Deployment

1. Once deployed, Render will show you a URL like: `https://chemistry-lab-simulator.onrender.com`
2. Click the URL to open your app
3. Test the following:
   - Homepage loads correctly
   - Can view chemicals
   - Can perform reactions (requires valid GOOGLE_API_KEY)

## Step 6: Update .env for Local Development

Update your local `backend/.env` file to match this format:

```env
GOOGLE_API_KEY=your_actual_api_key_here
DATABASE_URL=postgresql://postgres:1234@localhost:5432/chemlab
DB_HOST=localhost
DB_PORT=5432
DB_NAME=chemlab
DB_USER=postgres
DB_PASSWORD=1234
```

## Troubleshooting

### Build Fails

**Error: "No module named 'backend'"**
- Solution: Make sure your start command is: `gunicorn --bind 0.0.0.0:$PORT backend.app:app`

**Error: "Could not connect to database"**
- Solution: Verify DATABASE_URL is correctly set in environment variables
- Make sure you're using the **Internal Database URL** from Render

### App Crashes on Start

**Check logs:**
1. Go to your web service dashboard
2. Click "Logs" tab
3. Look for error messages

**Common issues:**
- Missing GOOGLE_API_KEY: The app will run but AI features won't work
- Database connection failed: Check DATABASE_URL format
- Port binding error: Make sure start command uses `$PORT` variable

### Database Tables Not Created

The app automatically creates tables on startup. If they're not created:

1. Check the logs for database connection errors
2. Verify DATABASE_URL is correct
3. You can manually initialize by:
   - Going to your web service dashboard
   - Click "Shell" tab
   - Run: `python -c "from backend.database import Database; db = Database(); db.create_tables()"`

## Free Tier Limitations

**Render Free Tier includes:**
- 750 hours/month of runtime
- App spins down after 15 minutes of inactivity
- First request after spin-down may take 30-60 seconds
- PostgreSQL database with 1GB storage
- 90-day expiration on free databases (you'll get email reminders)

**Important Notes:**
- Free services spin down with inactivity
- Database expires after 90 days (can be renewed for free)
- Upgrade to paid tier ($7/month) for 24/7 uptime

## Updating Your Deployment

When you make changes to your code:

```bash
git add .
git commit -m "Description of changes"
git push origin main
```

Render will automatically detect the push and redeploy your app!

## Alternative: Manual Deployment via Blueprint (render.yaml)

If you prefer infrastructure-as-code, you can use the included `render.yaml`:

1. Go to Render Dashboard
2. Click "New +" → "Blueprint"
3. Connect your GitHub repository
4. Render will detect `render.yaml` and create all resources
5. Add your GOOGLE_API_KEY in the environment variables after creation

## Support

If you encounter issues:
- Check Render documentation: https://render.com/docs
- View your app logs in the Render dashboard
- Verify all environment variables are set correctly
- Make sure your Google API key is valid

## Success!

Your Chemistry Lab Simulator is now live on the internet! 🎉

Share your URL with students and enjoy your free chemistry education platform.
