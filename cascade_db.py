# -*- coding: utf-8 -*-
"""
Project Cascade Database Schema and Operations
Standalone SQLite backend for cascade tracking
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / 'cascade_data.db'

def init_db():
    """Initialize database with schema"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Cascade Nodes
    c.execute('''CREATE TABLE IF NOT EXISTS cascade_nodes (
        node_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        mechanism TEXT NOT NULL,
        status TEXT DEFAULT 'inactive',
        amplitude REAL DEFAULT 0,
        frequency REAL DEFAULT 0,
        confidence REAL DEFAULT 0,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # Signals
    c.execute('''CREATE TABLE IF NOT EXISTS signals (
        signal_id INTEGER PRIMARY KEY,
        node_id INTEGER NOT NULL,
        domain TEXT,
        description TEXT,
        severity TEXT,
        date_recorded TIMESTAMP,
        source TEXT,
        status TEXT DEFAULT 'active',
        FOREIGN KEY(node_id) REFERENCES cascade_nodes(node_id)
    )''')

    # CASCADE Sequences
    c.execute('''CREATE TABLE IF NOT EXISTS cascade_sequences (
        cascade_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        node_sequence TEXT,
        confidence REAL,
        description TEXT,
        verified_instances TEXT,
        date_identified TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # Reference Points
    c.execute('''CREATE TABLE IF NOT EXISTS reference_points (
        point_id INTEGER PRIMARY KEY,
        metric_name TEXT NOT NULL,
        value REAL,
        date_recorded TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        category TEXT
    )''')

    # Baseline Return Failures
    c.execute('''CREATE TABLE IF NOT EXISTS baseline_failures (
        failure_id INTEGER PRIMARY KEY,
        geography TEXT,
        sector TEXT,
        mechanism TEXT,
        baseline_shift_percent REAL,
        date_recorded TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        source TEXT
    )''')

    # Daily Summaries
    c.execute('''CREATE TABLE IF NOT EXISTS daily_summaries (
        summary_id INTEGER PRIMARY KEY,
        date TIMESTAMP NOT NULL UNIQUE,
        content TEXT,
        signals_count INTEGER,
        findings TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # Daily Findings (structured entries from daily_findings.md)
    c.execute('''CREATE TABLE IF NOT EXISTS daily_findings (
        finding_id INTEGER PRIMARY KEY,
        date TEXT NOT NULL,
        overview TEXT,
        findings TEXT,
        methodological_insights TEXT,
        theoretical_advances TEXT,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # Amplitude Watch Log
    c.execute('''CREATE TABLE IF NOT EXISTS amplitude_watch (
        watch_id INTEGER PRIMARY KEY,
        node_id INTEGER NOT NULL,
        node_name TEXT,
        current_amplitude REAL,
        previous_amplitude REAL,
        escalation_rate TEXT,
        confidence TEXT,
        risk_threshold REAL,
        measurement_basis TEXT,
        breakpoint TEXT,
        evidence TEXT,
        status TEXT,
        date_recorded TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(node_id) REFERENCES cascade_nodes(node_id)
    )''')

    # Project Goals
    c.execute('''CREATE TABLE IF NOT EXISTS project_goals (
        goal_id INTEGER PRIMARY KEY,
        goal_text TEXT NOT NULL,
        status TEXT DEFAULT 'active',
        category TEXT,
        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        amended_date TIMESTAMP,
        retired_date TIMESTAMP,
        notes TEXT
    )''')

    # Systematic Underestimation
    c.execute('''CREATE TABLE IF NOT EXISTS systematic_underestimation (
        finding_id INTEGER PRIMARY KEY,
        domain TEXT NOT NULL,
        category TEXT NOT NULL,
        finding_text TEXT NOT NULL,
        severity TEXT DEFAULT 'moderate',
        underestimation_factor TEXT,
        actual_vs_predicted TEXT,
        evidence_text TEXT,
        source TEXT,
        date_recorded TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'active'
    )''')

    # Research Findings (organized by mechanism)
    c.execute('''CREATE TABLE IF NOT EXISTS research_findings (
        finding_id INTEGER PRIMARY KEY,
        mechanism TEXT NOT NULL,
        finding_text TEXT NOT NULL,
        confidence_level REAL DEFAULT 0.7,
        date_discovered TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        supporting_evidence TEXT,
        related_signals TEXT,
        significance TEXT,
        status TEXT DEFAULT 'active'
    )''')

    # Gmail Message Tracking (for Routine 1 - all emails analysis)
    c.execute('''CREATE TABLE IF NOT EXISTS gmail_messages_analyzed (
        message_id TEXT PRIMARY KEY,
        folder TEXT,
        sender TEXT,
        subject TEXT,
        date_received TIMESTAMP,
        signals_extracted INTEGER DEFAULT 0,
        findings_extracted INTEGER DEFAULT 0,
        date_analyzed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    conn.commit()
    conn.close()

def get_connection():
    """Get database connection"""
    return sqlite3.connect(DB_PATH)

def get_all_nodes():
    """Retrieve all cascade nodes"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM cascade_nodes ORDER BY node_id')
    nodes = [dict(row) for row in c.fetchall()]
    conn.close()
    return nodes

def get_node_signals(node_id):
    """Get all signals for a node"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM signals WHERE node_id = ? ORDER BY date_recorded DESC', (node_id,))
    signals = [dict(row) for row in c.fetchall()]
    conn.close()
    return signals

def get_all_signals(limit=None):
    """Retrieve all signals"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    if limit:
        c.execute('SELECT * FROM signals ORDER BY date_recorded DESC LIMIT ?', (limit,))
    else:
        c.execute('SELECT * FROM signals ORDER BY date_recorded DESC')
    signals = [dict(row) for row in c.fetchall()]
    conn.close()
    return signals

def get_cascade_sequences():
    """Retrieve all CASCADE sequences"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM cascade_sequences ORDER BY cascade_id')
    sequences = [dict(row) for row in c.fetchall()]
    conn.close()
    return sequences

def get_reference_points():
    """Retrieve reference point metrics"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT DISTINCT metric_name, value, date_recorded FROM reference_points ORDER BY date_recorded DESC')
    points = [dict(row) for row in c.fetchall()]
    conn.close()
    return points

def add_reference_point(metric_name, value, category=None, date_recorded=None):
    """Add a reference point metric"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('''INSERT INTO reference_points (metric_name, value, category, date_recorded)
                 VALUES (?, ?, ?, COALESCE(?, CURRENT_TIMESTAMP))''',
              (metric_name, value, category, date_recorded))
    conn.commit()
    point_id = c.lastrowid
    conn.close()
    return point_id

def get_baseline_failures():
    """Retrieve baseline return failures by geography/sector"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM baseline_failures ORDER BY date_recorded DESC')
    failures = [dict(row) for row in c.fetchall()]
    conn.close()
    return failures

def get_daily_summary(date):
    """Get summary for specific date"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM daily_summaries WHERE DATE(date) = DATE(?)', (date,))
    summary = c.fetchone()
    conn.close()
    return dict(summary) if summary else None

def add_signal(node_id, domain, description, severity, date_recorded, source):
    """Add a signal"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('''INSERT INTO signals (node_id, domain, description, severity, date_recorded, source)
                 VALUES (?, ?, ?, ?, ?, ?)''',
              (node_id, domain, description, severity, date_recorded, source))
    conn.commit()
    signal_id = c.lastrowid
    conn.close()
    return signal_id

def update_node_amplitude(node_id, amplitude):
    """Update node amplitude"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('UPDATE cascade_nodes SET amplitude = ?, last_updated = CURRENT_TIMESTAMP WHERE node_id = ?',
              (amplitude, node_id))
    conn.commit()
    conn.close()

def update_node_frequency(node_id, frequency):
    """Update node frequency"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('UPDATE cascade_nodes SET frequency = ?, last_updated = CURRENT_TIMESTAMP WHERE node_id = ?',
              (frequency, node_id))
    conn.commit()
    conn.close()

def get_metrics_summary():
    """Get summary metrics for dashboard"""
    conn = get_connection()
    c = conn.cursor()

    total_signals = c.execute('SELECT COUNT(*) FROM signals').fetchone()[0]
    active_nodes = c.execute('SELECT COUNT(*) FROM cascade_nodes WHERE status = "active"').fetchone()[0]
    cascade_sequences = c.execute('SELECT COUNT(*) FROM cascade_sequences').fetchone()[0]

    conn.close()

    return {
        'total_signals': total_signals,
        'active_nodes': active_nodes,
        'cascade_sequences': cascade_sequences
    }

def get_daily_findings(date_str=None):
    """Get daily findings for a specific date or today"""
    from datetime import datetime

    if date_str is None:
        date_str = datetime.now().strftime('%Y-%m-%d')

    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM daily_findings WHERE date = ?', (date_str,))
    result = c.fetchone()
    conn.close()
    return dict(result) if result else None

def add_or_update_daily_findings(date_str, overview, findings, methodological_insights, theoretical_advances):
    """Add or update daily findings"""
    conn = get_connection()
    c = conn.cursor()

    # Check if entry exists
    existing = c.execute('SELECT finding_id FROM daily_findings WHERE date = ?', (date_str,)).fetchone()

    if existing:
        c.execute('''UPDATE daily_findings
                     SET overview = ?, findings = ?, methodological_insights = ?,
                         theoretical_advances = ?, last_updated = CURRENT_TIMESTAMP
                     WHERE date = ?''',
                  (overview, findings, methodological_insights, theoretical_advances, date_str))
    else:
        c.execute('''INSERT INTO daily_findings
                     (date, overview, findings, methodological_insights, theoretical_advances)
                     VALUES (?, ?, ?, ?, ?)''',
                  (date_str, overview, findings, methodological_insights, theoretical_advances))

    conn.commit()
    conn.close()

def get_nodes_by_activity():
    """Get all nodes ranked by signal count and severity"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    query = '''
    SELECT n.node_id, n.name, n.status, n.amplitude, n.frequency, n.confidence,
           COUNT(s.signal_id) as signal_count,
           SUM(CASE WHEN s.severity = 'critical' THEN 3
                    WHEN s.severity = 'serious' THEN 2
                    WHEN s.severity = 'warning' THEN 1 ELSE 0 END) as severity_score
    FROM cascade_nodes n
    LEFT JOIN signals s ON n.node_id = s.node_id
    GROUP BY n.node_id
    ORDER BY signal_count DESC, severity_score DESC
    '''

    c.execute(query)
    nodes = [dict(row) for row in c.fetchall()]
    conn.close()
    return nodes

def get_cascade_sequences_with_signals():
    """Get CASCADE sequences and their real-world activation status"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    sequences = c.execute('''
        SELECT cs.cascade_id, cs.name, cs.node_sequence, cs.confidence,
               COUNT(DISTINCT s.signal_id) as signal_count
        FROM cascade_sequences cs
        LEFT JOIN signals s ON s.node_id IN (
            SELECT CAST(value AS INTEGER) FROM json_each('[' ||
            REPLACE(cs.node_sequence, '->', ',') || ']')
        )
        GROUP BY cs.cascade_id
        ORDER BY signal_count DESC
    ''').fetchall()

    result = [dict(row) for row in sequences]
    conn.close()
    return result

def get_geographic_hotspots():
    """Get baseline return failures by geography - hotspots of system stress"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute('''
        SELECT geography, COUNT(*) as failure_count,
               AVG(baseline_shift_percent) as avg_shift,
               MIN(baseline_shift_percent) as min_shift,
               MAX(baseline_shift_percent) as max_shift
        FROM baseline_failures
        GROUP BY geography
        ORDER BY failure_count DESC, avg_shift DESC
    ''')

    hotspots = [dict(row) for row in c.fetchall()]
    conn.close()
    return hotspots

def get_system_robustness_trajectory():
    """Get system robustness over time to show degradation trend"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute('''
        SELECT metric_name, value, date_recorded
        FROM reference_points
        WHERE metric_name LIKE '%Robustness%'
        ORDER BY date_recorded
    ''')

    trajectory = [dict(row) for row in c.fetchall()]
    conn.close()
    return trajectory

def get_all_reference_points_latest():
    """Get latest value for each reference metric"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute('''
        SELECT DISTINCT metric_name, value, date_recorded
        FROM reference_points
        WHERE date_recorded = (
            SELECT MAX(date_recorded) FROM reference_points rp2
            WHERE rp2.metric_name = reference_points.metric_name
        )
        ORDER BY metric_name
    ''')

    points = [dict(row) for row in c.fetchall()]
    conn.close()
    return points

def get_amplitude_watch():
    """Retrieve all amplitude watch log entries"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM amplitude_watch ORDER BY node_id')
    entries = [dict(row) for row in c.fetchall()]
    conn.close()
    return entries

def get_amplitude_watch_by_status(status):
    """Get amplitude watch entries filtered by status (ACCELERATING, STRUCTURAL, etc)"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM amplitude_watch WHERE status = ? ORDER BY current_amplitude DESC', (status,))
    entries = [dict(row) for row in c.fetchall()]
    conn.close()
    return entries

# ============================================
# PROJECT GOALS MANAGEMENT
# ============================================

def retire_goal(goal_id, notes=''):
    """Retire a goal (mark as inactive)"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('''UPDATE project_goals
                 SET status = ?, retired_date = CURRENT_TIMESTAMP, notes = ?
                 WHERE goal_id = ?''',
              ('retired', notes, goal_id))
    conn.commit()
    conn.close()

def activate_goal(goal_id):
    """Reactivate a retired goal"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('''UPDATE project_goals
                 SET status = ?, retired_date = NULL
                 WHERE goal_id = ?''',
              ('active', goal_id))
    conn.commit()
    conn.close()

# ============================================
# SYSTEMATIC UNDERESTIMATION TRACKING
# ============================================

def get_all_underestimations(domain=None, status_filter='active'):
    """Get systematic underestimation findings, optionally filtered by domain"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    if domain:
        c.execute('''SELECT * FROM systematic_underestimation
                     WHERE status = ? AND domain = ?
                     ORDER BY date_recorded DESC''', (status_filter, domain))
    else:
        c.execute('''SELECT * FROM systematic_underestimation
                     WHERE status = ?
                     ORDER BY date_recorded DESC''', (status_filter,))

    findings = [dict(row) for row in c.fetchall()]
    conn.close()
    return findings

def get_underestimations_by_category(category):
    """Get underestimation findings by category"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('''SELECT * FROM systematic_underestimation
                 WHERE category = ? AND status = 'active'
                 ORDER BY severity DESC, date_recorded DESC''', (category,))
    findings = [dict(row) for row in c.fetchall()]
    conn.close()
    return findings

def add_underestimation(domain, category, finding_text, severity='moderate',
                       underestimation_factor=None, actual_vs_predicted=None,
                       evidence_text=None, source=None):
    """Add a new systematic underestimation finding"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('''INSERT INTO systematic_underestimation
                 (domain, category, finding_text, severity, underestimation_factor,
                  actual_vs_predicted, evidence_text, source, status)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (domain, category, finding_text, severity, underestimation_factor,
               actual_vs_predicted, evidence_text, source, 'active'))
    conn.commit()
    finding_id = c.lastrowid
    conn.close()
    return finding_id

def get_underestimation_domains():
    """Get list of unique domains"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('''SELECT DISTINCT domain FROM systematic_underestimation
                 WHERE status = 'active' ORDER BY domain''')
    domains = [row[0] for row in c.fetchall()]
    conn.close()
    return domains

def get_underestimation_summary():
    """Get summary statistics on underestimation"""
    conn = get_connection()
    c = conn.cursor()

    total = c.execute('SELECT COUNT(*) FROM systematic_underestimation WHERE status = "active"').fetchone()[0]

    severity_critical = c.execute('SELECT COUNT(*) FROM systematic_underestimation WHERE status = "active" AND severity = "critical"').fetchone()[0]
    severity_serious = c.execute('SELECT COUNT(*) FROM systematic_underestimation WHERE status = "active" AND severity = "serious"').fetchone()[0]
    severity_moderate = c.execute('SELECT COUNT(*) FROM systematic_underestimation WHERE status = "active" AND severity = "moderate"').fetchone()[0]

    domains = c.execute('SELECT COUNT(DISTINCT domain) FROM systematic_underestimation WHERE status = "active"').fetchone()[0]
    categories = c.execute('SELECT COUNT(DISTINCT category) FROM systematic_underestimation WHERE status = "active"').fetchone()[0]

    conn.close()

    return {
        'total_findings': total,
        'critical': severity_critical,
        'serious': severity_serious,
        'moderate': severity_moderate,
        'unique_domains': domains,
        'unique_categories': categories
    }

# ============================================
# RESEARCH FINDINGS MANAGEMENT
# ============================================

def get_all_findings(status_filter='active', mechanism=None):
    """Get all research findings, optionally filtered by mechanism or status"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    if mechanism:
        c.execute('''SELECT * FROM research_findings
                     WHERE status = ? AND mechanism = ?
                     ORDER BY confidence_level DESC, date_discovered DESC''',
                  (status_filter, mechanism))
    else:
        c.execute('''SELECT * FROM research_findings
                     WHERE status = ?
                     ORDER BY confidence_level DESC, date_discovered DESC''',
                  (status_filter,))

    findings = [dict(row) for row in c.fetchall()]
    conn.close()
    return findings

def get_findings_by_mechanism():
    """Get findings grouped by mechanism"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute('''SELECT mechanism, COUNT(*) as count,
                        AVG(confidence_level) as avg_confidence,
                        MAX(date_discovered) as latest_date
                 FROM research_findings
                 WHERE status = 'active'
                 GROUP BY mechanism
                 ORDER BY count DESC, avg_confidence DESC''')

    mechanisms = [dict(row) for row in c.fetchall()]
    conn.close()
    return mechanisms

def add_finding(mechanism, finding_text, confidence_level=0.7, supporting_evidence=None,
               related_signals=None, significance=None):
    """Add a new research finding"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('''INSERT INTO research_findings
                 (mechanism, finding_text, confidence_level, supporting_evidence,
                  related_signals, significance, status)
                 VALUES (?, ?, ?, ?, ?, ?, ?)''',
              (mechanism, finding_text, confidence_level, supporting_evidence,
               related_signals, significance, 'active'))
    conn.commit()
    finding_id = c.lastrowid
    conn.close()
    return finding_id

def update_finding(finding_id, finding_text=None, confidence_level=None):
    """Update a research finding"""
    conn = get_connection()
    c = conn.cursor()

    if finding_text and confidence_level:
        c.execute('''UPDATE research_findings
                     SET finding_text = ?, confidence_level = ?
                     WHERE finding_id = ?''',
                  (finding_text, confidence_level, finding_id))
    elif finding_text:
        c.execute('''UPDATE research_findings
                     SET finding_text = ?
                     WHERE finding_id = ?''',
                  (finding_text, finding_id))
    elif confidence_level:
        c.execute('''UPDATE research_findings
                     SET confidence_level = ?
                     WHERE finding_id = ?''',
                  (confidence_level, finding_id))

    conn.commit()
    conn.close()

def retire_finding(finding_id):
    """Retire a research finding"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('UPDATE research_findings SET status = ? WHERE finding_id = ?',
              ('retired', finding_id))
    conn.commit()
    conn.close()

def get_mechanisms_list():
    """Get list of all mechanisms"""
    return [
        'Threshold Dynamics',
        'Feedback Amplification',
        'Institutional Lag',
        'Measurement & Uncertainty',
        'Tipping Points & Bifurcation',
        'Coupling & Interdependence',
        'Socioeconomic Constraints',
        'Information Asymmetry'
    ]

def get_findings_summary():
    """Get summary statistics on research findings"""
    conn = get_connection()
    c = conn.cursor()

    total = c.execute('SELECT COUNT(*) FROM research_findings WHERE status = "active"').fetchone()[0]
    avg_confidence = c.execute('SELECT AVG(confidence_level) FROM research_findings WHERE status = "active"').fetchone()[0]
    mechanisms = c.execute('SELECT COUNT(DISTINCT mechanism) FROM research_findings WHERE status = "active"').fetchone()[0]

    conn.close()

    return {
        'total_findings': total,
        'avg_confidence': avg_confidence or 0.0,
        'unique_mechanisms': mechanisms
    }

def add_goal(goal_text, category=None, notes=None):
    """Add a new project goal"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('''INSERT INTO project_goals (goal_text, status, category, notes)
                 VALUES (?, ?, ?, ?)''',
              (goal_text, 'active', category, notes))
    conn.commit()
    goal_id = c.lastrowid
    conn.close()
    return goal_id

def get_all_goals(status='active'):
    """Get all project goals, optionally filtered by status"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    if status:
        c.execute('SELECT * FROM project_goals WHERE status = ? ORDER BY goal_id', (status,))
    else:
        c.execute('SELECT * FROM project_goals ORDER BY goal_id')
    goals = [dict(row) for row in c.fetchall()]
    conn.close()
    return goals

def update_goal(goal_id, goal_text=None, category=None, notes=None):
    """Update an existing project goal"""
    conn = get_connection()
    c = conn.cursor()

    updates = []
    params = []

    if goal_text is not None:
        updates.append('goal_text = ?')
        params.append(goal_text)
    if category is not None:
        updates.append('category = ?')
        params.append(category)
    if notes is not None:
        updates.append('notes = ?')
        params.append(notes)

    if updates:
        updates.append('amended_date = CURRENT_TIMESTAMP')
        params.append(goal_id)
        query = 'UPDATE project_goals SET ' + ', '.join(updates) + ' WHERE goal_id = ?'
        c.execute(query, params)
        conn.commit()

    conn.close()

# ============================================
# GMAIL MESSAGE TRACKING (Routine 1)
# ============================================

def is_message_analyzed(message_id):
    """Check if a Gmail message has already been analyzed"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT 1 FROM gmail_messages_analyzed WHERE message_id = ?', (message_id,))
    result = c.fetchone() is not None
    conn.close()
    return result

def mark_message_analyzed(message_id, folder, sender, subject, date_received, signals_count=0, findings_count=0):
    """Mark a Gmail message as analyzed"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('''INSERT OR IGNORE INTO gmail_messages_analyzed
                 (message_id, folder, sender, subject, date_received, signals_extracted, findings_extracted)
                 VALUES (?, ?, ?, ?, ?, ?, ?)''',
              (message_id, folder, sender, subject, date_received, signals_count, findings_count))
    conn.commit()
    conn.close()

def get_analyzed_messages_count():
    """Get total number of analyzed messages"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM gmail_messages_analyzed')
    count = c.fetchone()[0]
    conn.close()
    return count

if __name__ == '__main__':
    init_db()
    print(f"Database initialized at {DB_PATH}")
