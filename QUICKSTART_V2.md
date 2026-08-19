# Project Cascade v2 — Quick Start

## Fastest Path to Production (5 minutes)

### Step 1: Create GitHub Repository
1. Go to https://github.com/new
2. Repository name: `Project-Cascade-v2`
3. Description: `Clean deployment with goal-driven routines`
4. Make it **Public** (required for Streamlit Cloud)
5. Click "Create repository"

### Step 2: Push Code
```bash
# From your Project-Cascade-v2 folder (with all the files)
git init
git add .
git commit -m "Initial commit: Project Cascade v2"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/Project-Cascade-v2.git
git push -u origin main
```

### Step 3: Deploy to Streamlit Cloud
1. Go to https://share.streamlit.io/
2. Click **New app**
3. Repository: `YOUR_USERNAME/Project-Cascade-v2`
4. Branch: `main`
5. Main file: `cascade_app.py`
6. Click **Deploy**

**Done!** Streamlit will deploy within 1-2 minutes.

---

## First Run Checklist

After deployment:
- [ ] App loads without errors
- [ ] Summary page displays
- [ ] Project Goals tab opens (contains 13 cascade nodes)
- [ ] Today's Progress section visible
- [ ] System Mechanism Tracker renders

## Known Issue to Fix

If you see **ValueError** in Project Goals tab when editing goals:
→ See `KNOWN_ISSUES.md` for the one-line fix

Apply the fix, commit, push—Streamlit auto-redeploys.

## Setting Up Routines (Optional)

Routines can run locally or via cloud-based scheduled triggers.

**Local Testing:**
```bash
python routines/import_daily_news_headlines.py
python routines/import_substack_imap.py
python routines/import_daily_infrastructure.py
python routines/import_institutional_data.py
```

**Production (Cloud Scheduled Triggers):**
Use Claude Code Remote or similar to schedule:
- Routine 0 (News): Hourly at :24 past UTC
- Routine 1 (Gmail): Hourly at :48 past UTC
- Routine 2 (Infrastructure): Daily 09:00 UTC
- Routine 3 (Institutional): Daily 09:00 UTC

---

## Rollback to v1

If needed, v1 remains at your original GitHub repo. Just point Streamlit Cloud back there.

---

**Questions?** Check README.md and KNOWN_ISSUES.md

