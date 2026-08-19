# Project Cascade v2 - Clean Deployment

This is a fresh deployment of Project Cascade with all improvements from the morning session preserved.

## What's Included

**Dashboard Features:**
- Summary (Planetary Degradation Monitor) at top of navigation
- Project Goals with framework section (13 cascade nodes)
- Today's Progress with auto-generated routine output
- System Mechanism Tracker with cascade node visualization
- Complete navigation reorganization

**Routines (Goal-Driven Analysis):**
- Routine 0: Hourly news headline analysis (import_daily_news_headlines.py)
- Routine 1: Hourly Gmail analysis (import_substack_imap.py)
- Routine 2: Daily infrastructure monitoring (import_daily_infrastructure.py)
- Routine 3: Daily institutional data synthesis (import_institutional_data.py)

All routines:
- Load project goals from database at runtime
- Score content against goals
- Extract cascade-relevant signals
- Generate findings with confidence scores
- Include fallback dependency installation for cloud execution

## Deployment Instructions

### 1. Create GitHub Repository
```bash
# Create new repo on GitHub
# Name: Project-Cascade-v2
# Description: Clean deployment with goal-driven routines and reorganized dashboard
# Make it public

# Clone the new repo locally
git clone https://github.com/YOUR_USERNAME/Project-Cascade-v2.git
cd Project-Cascade-v2
```

### 2. Add Files
Copy all files from this folder into your repo:
- `cascade_app.py` (main dashboard)
- `cascade_db.py` (database functions)
- `requirements.txt` (Python dependencies)
- `routines/` folder with all four routines

### 3. Commit & Push
```bash
git add .
git commit -m "Initial commit: Project Cascade v2 with goal-driven routines and reorganized dashboard"
git push origin main
```

### 4. Deploy to Streamlit Cloud
1. Go to https://share.streamlit.io/
2. Click "New app"
3. Select your GitHub repo: `Project-Cascade-v2`
4. Main file: `cascade_app.py`
5. Deploy!

Streamlit will automatically redeploy whenever you push changes to main.

## Known Issues & Fixes

See `KNOWN_ISSUES.md` for the one documented issue (ValueError in goal editing) and its fix.

## Database Setup

First run will create `cascade_data.db` with tables:
- cascade_nodes (13 mechanisms)
- project_goals (goal management)
- signals (routine output)
- findings (analysis results)
- daily_findings (manual captures)
- gmail_messages_analyzed (deduplication tracking)

## Scheduled Routines

When ready, set up cloud-based scheduled triggers for:
- Routine 0 (News): Hourly at :24 past UTC
- Routine 1 (Gmail): Hourly at :48 past UTC
- Routine 2 (Infrastructure): Daily 09:00 UTC
- Routine 3 (Institutional): Daily 09:00 UTC

Or keep them as manual imports for now and test locally first.

## Support

For issues:
1. Check KNOWN_ISSUES.md
2. Verify requirements.txt installs correctly
3. Check Streamlit Cloud logs for import/dependency errors
4. Confirm cascade_data.db is created in first run

---

**Version:** 2.0 (Fresh deployment, morning session improvements preserved)
**Created:** 2026-08-19
