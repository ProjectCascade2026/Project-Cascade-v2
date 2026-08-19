# Known Issues & Fixes

## Issue: ValueError in Goal Editing (cascade_app.py, line ~1156)

**Symptom:** App crashes with error when navigating to "Project Goals" tab and trying to edit a goal:
```
ValueError: list.index(x): x not in list
```

**Root Cause:** The goal category index lookup fails when:
- A goal's category value is None
- A goal's category doesn't exist in the allowed list: `["primary", "secondary", "supporting", "monitoring"]`
- Database contains legacy/malformed category data

**Location:** cascade_app.py, in `section_project_goals()` function, goal editing section (line ~1156)

**Fix (Apply Once):**

In cascade_app.py, find the goal editing section (around line 1153-1166). Replace:

```python
# OLD CODE (BROKEN):
edited_text = st.text_area("Goal Text", value=goal_to_edit['goal_text'], height=100, key=f"goal_text_{goal_to_edit['goal_id']}")
edited_category = st.selectbox("Category",
                               ["primary", "secondary", "supporting", "monitoring"],
                               index=["primary", "secondary", "supporting", "monitoring"].index(goal_to_edit['category'].lower()),
                               key=f"goal_cat_{goal_to_edit['goal_id']}")
```

With:

```python
# NEW CODE (FIXED):
edited_text = st.text_area("Goal Text", value=goal_to_edit['goal_text'], height=100, key=f"goal_text_{goal_to_edit['goal_id']}")

# Safe category index lookup with fallback
category_list = ["primary", "secondary", "supporting", "monitoring"]
current_category = (goal_to_edit['category'] or "secondary").lower()
try:
    category_index = category_list.index(current_category)
except ValueError:
    category_index = 0  # default to "primary" if category not found

edited_category = st.selectbox("Category",
                               category_list,
                               index=category_index,
                               key=f"goal_cat_{goal_to_edit['goal_id']}")
```

**What This Does:**
- Safely handles None values in goal category
- Falls back to "primary" category if stored value is invalid
- Prevents crashes when database contains malformed data
- Allows smooth goal editing without exceptions

**After Fixing:**
1. Commit the change: `git commit -m "Fix: Safe category index handling in goal editing"`
2. Push to GitHub: `git push origin main`
3. Streamlit Cloud will auto-redeploy
4. App should load without ValueError in Project Goals tab

---

## No Other Known Issues

All other functionality tested and working:
- Dashboard navigation ✓
- Summary page ✓
- Today's Progress ✓
- System Mechanism Tracker ✓
- Routines (when executed) ✓
- Database queries ✓

---

**If you encounter other issues:**
1. Check Streamlit Cloud logs for import/dependency errors
2. Verify all Python packages install correctly: `pip install -r requirements.txt`
3. Confirm cascade_data.db is created on first run
4. Check that Google Drive/Gmail API credentials are configured (if using those routines)

