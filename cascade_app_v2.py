# -*- coding: utf-8 -*-
"""
Project Cascade Standalone Application
Streamlit-based dashboard with 8 primary sections
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import subprocess
import os
from cascade_db import (
    get_all_nodes, get_all_signals, get_cascade_sequences,
    get_reference_points, get_baseline_failures, get_metrics_summary,
    get_node_signals, get_daily_findings, get_nodes_by_activity,
    get_cascade_sequences_with_signals, get_geographic_hotspots,
    get_system_robustness_trajectory, get_all_reference_points_latest,
    get_amplitude_watch, get_amplitude_watch_by_status,
    get_all_goals, add_goal, update_goal, retire_goal, activate_goal,
    get_all_underestimations, get_underestimations_by_category, add_underestimation,
    get_underestimation_domains, get_underestimation_summary,
    get_all_findings, get_findings_by_mechanism, add_finding, get_mechanisms_list, get_findings_summary
)
import json

# Page config
st.set_page_config(
    page_title="Project Cascade",
    page_icon="[CHART]",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom theme
st.markdown("""
    <style>
    :root {
        --surface-1: #1a1a19;
        --text-primary: #ffffff;
        --text-secondary: #c3c2b7;
        --series-1: #3987e5;
    }
    body {
        background-color: #0d0d0d;
        color: #ffffff;
        font-size: 18px;
    }

    /* Increase font sizes globally by +2 */
    h1 { font-size: 2.5em !important; }
    h2 { font-size: 2.0em !important; }
    h3 { font-size: 1.75em !important; }
    p, li, div { font-size: 18px !important; }

    /* Highlight for recent additions */
    .highlight-recent {
        background-color: #8B6F47;
        padding: 12px;
        border-radius: 6px;
        margin: 8px 0;
        border-left: 4px solid #D4A574;
        color: #f0f0f0;
    }

    .highlight-recent strong {
        color: #ffffff;
    }
    </style>
    """, unsafe_allow_html=True)

def metric_card(label, value, trend=None, color="#3987e5"):
    """Render a metric card"""
    col1, col2 = st.columns([3, 1])
    with col1:
        st.metric(label, value)
    if trend:
        with col2:
            st.caption(trend)

# ============================================
# 1. SUMMARY
# ============================================
def section_summary():
    st.header("Planetary Degradation Monitor")

    try:
        # Get all data with safe handling
        metrics = get_metrics_summary() or {}
        nodes_by_activity = get_nodes_by_activity() or []
        cascades_with_signals = get_cascade_sequences_with_signals() or []
        hotspots = get_geographic_hotspots() or []
        reference_points = get_all_reference_points_latest() or []

        # Executive Summary Metrics (Top Row)
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric("Total Signals", metrics.get('total_signals', 0))
        with col2:
            active_count = len([n for n in nodes_by_activity if n.get('signal_count') and n['signal_count'] > 0])
            st.metric("Active Nodes", active_count)
        with col3:
            st.metric("CASCADE Sequences", metrics.get('cascade_sequences', 0))
        with col4:
            st.metric("Geographic Hotspots", len(hotspots))
        with col5:
            robustness = next((rp.get('value', 0) for rp in reference_points if rp and 'Robustness' in rp.get('metric_name', '')), 0)
            st.metric("System Robustness", f"{robustness:.0f}%")

    except Exception as e:
        st.error(f"Error loading summary metrics: {str(e)}")

    st.divider()

    # Meta-Summary: State of the Planet
    try:
        st.subheader("State of the Planet — Meta-Assessment")

        # Generate dynamic meta-summary with safe fallbacks
        active_mechanisms = len([n for n in nodes_by_activity if n.get('signal_count') and n['signal_count'] > 0]) if nodes_by_activity else 0
        total_signals = metrics.get('total_signals', 0) if metrics else 0
        robustness_value = next((float(rp.get('value', 0)) for rp in reference_points if rp and 'Robustness' in rp.get('metric_name', '')), 0) if reference_points else 0
        hotspot_count = len(hotspots) if hotspots else 0
        cascade_count = metrics.get('cascade_sequences', 0) if metrics else 0

        # Determine urgency level based on metrics
        if robustness_value < 40 or active_mechanisms >= 10:
            urgency = "CRITICAL"
            urgency_indicator = "[CRITICAL]"
        elif robustness_value < 60 or active_mechanisms >= 8:
            urgency = "HIGH"
            urgency_indicator = "[HIGH]"
        else:
            urgency = "ELEVATED"
            urgency_indicator = "[ELEVATED]"

        meta_summary = f"""
        **Urgency Level: {urgency_indicator}** | {active_mechanisms} active cascade mechanisms | System robustness at {robustness_value:.0f}%

        Planetary systems show persistent degradation across {active_mechanisms} tracked failure mechanisms. {total_signals} documented signals
        reveal {cascade_count} active cascade sequences with confirmed real-world activation. Geographic concentration in {hotspot_count} hotspots indicates
        regional tipping points approaching. Infrastructure brittleness, supply chain fragility, and measurement capacity erosion amplify
        feedback loops. Economic depletion reducing adaptive capacity. System unable to return to baseline—baseline itself shifting.
        Institutional coordination failures compound response lags. Current trajectory suggests critical threshold crossings likely within 2-3 years.
        """

        st.markdown(meta_summary)
        st.caption("Last updated: " + datetime.now().strftime("%Y-%m-%d %H:%M UTC") + " | Assessment based on active signal patterns and cascade node activation")

    except Exception as e:
        st.warning(f"Meta-assessment temporarily unavailable: {str(e)}")

    st.divider()

    # Section 1: Top Activated Nodes (Ranked by Signal Count & Severity)
    st.subheader("[CRITICAL] Top Activated Cascade Nodes")
    st.caption("Ranked by signal frequency and severity — nodes with greatest real-world activation")

    active_nodes = [n for n in nodes_by_activity if n['signal_count'] and n['signal_count'] > 0]
    if active_nodes:
        node_display = []
        for node in active_nodes[:8]:  # Top 8
            node_display.append({
                'Node': f"Node {node['node_id']}",
                'Mechanism': node['name'],
                'Signals': node['signal_count'] or 0,
                'Severity': node['severity_score'] or 0,
                'Amplitude': f"{node['amplitude']:.1f}" if node['amplitude'] else "—",
                'Frequency': f"{node['frequency']:.1f}" if node['frequency'] else "—"
            })

        node_df = pd.DataFrame(node_display)
        st.dataframe(node_df, width='stretch', hide_index=True)
    else:
        st.info("No active nodes currently being tracked")

    st.divider()

    # Section 2: Active CASCADE Sequences with Real-World Confirmations
    st.subheader("[LINK] Active CASCADE Sequences")
    st.caption("CASCADE pathways showing real-world activation — documented causal chains")

    if cascades_with_signals:
        cascade_display = []
        for cs in cascades_with_signals[:10]:
            cascade_display.append({
                'ID': f"CASCADE {cs['cascade_id']}",
                'Node Chain': cs['node_sequence'],
                'Real-World Signals': cs['signal_count'] or 0,
                'Confidence': f"{cs['confidence']:.0%}" if cs['confidence'] else "—"
            })

        cascade_df = pd.DataFrame(cascade_display)
        st.dataframe(cascade_df, width='stretch', hide_index=True)
    else:
        st.info("No CASCADE sequences with signals yet")

    st.divider()

    # Section 3: Geographic Hotspots of Baseline Return Failures
    st.subheader("[WORLD] Geographic Hotspots — Baseline Return Failure Expansion")
    st.caption("Regions/sectors showing persistent inability to return to pre-disaster baseline")

    if hotspots:
        hotspot_display = []
        for spot in hotspots:
            hotspot_display.append({
                'Region/Sector': spot['geography'],
                'Failures Documented': spot['failure_count'],
                'Avg Baseline Shift %': f"{spot['avg_shift']:.1f}%",
                'Range': f"{spot['min_shift']:.0f}% to {spot['max_shift']:.0f}%"
            })

        hotspot_df = pd.DataFrame(hotspot_display)
        st.dataframe(hotspot_df, width='stretch', hide_index=True)
    else:
        st.info("No baseline failures documented yet")

    st.divider()

    # Section 4: System Robustness Trajectory
    st.subheader("[DOWN] System Robustness Trajectory")
    st.caption("Degradation trend — is system adaptive capacity declining?")

    robustness_data = get_system_robustness_trajectory()
    if robustness_data:
        robust_df = pd.DataFrame(robustness_data)
        robust_df['date_recorded'] = pd.to_datetime(robust_df['date_recorded'])

        fig = px.line(robust_df, x='date_recorded', y='value',
                     title="System Robustness Over Time",
                     markers=True)
        fig.update_layout(height=300)
        fig.update_xaxes(title_text="Date")
        fig.update_yaxes(title_text="Robustness Index (%)")
        st.plotly_chart(fig)
    else:
        st.info("Insufficient robustness data for trend analysis")

    st.divider()

    # Section 5: Reference Points (System-Level Metrics)
    st.subheader("[CHART] System-Level Reference Points")
    st.caption("Amplitude, Frequency, Interconnectedness, Underestimation, and Robustness metrics")

    if reference_points:
        ref_display = []
        for rp in reference_points:
            ref_display.append({
                'Metric': rp['metric_name'],
                'Value': f"{rp['value']:.1f}",
                'Last Updated': rp['date_recorded']
            })

        ref_df = pd.DataFrame(ref_display)
        st.dataframe(ref_df, width='stretch', hide_index=True)
    else:
        st.info("No reference points recorded yet")

    st.divider()

    # Section 6: Recent Signals (Last 20)
    st.subheader("[POINT] Recent Signals (Last 20)")
    st.caption("Latest cascade mechanism activations — ordered by date")

    signals = get_all_signals(limit=20)
    if signals:
        signals_df = pd.DataFrame(signals)
        signals_df['date_recorded'] = pd.to_datetime(signals_df['date_recorded'])
        display_cols = ['node_id', 'domain', 'severity', 'source', 'date_recorded']
        signals_df = signals_df[display_cols]
        signals_df.columns = ['Node', 'Domain', 'Severity', 'Source', 'Date']
        st.dataframe(signals_df, width='stretch', hide_index=True)
    else:
        st.info("No signals recorded yet")

# ============================================
# 2. TODAY'S PROGRESS
# ============================================
def section_today_progress():
    st.header("[UP] Today's Progress")

    today_str = datetime.now().strftime('%Y-%m-%d')

    # ============================================
    # SECTION 1: AUTO-GENERATED SYNTHESIS FROM ROUTINES
    # ============================================
    st.subheader("[AI] Auto-Synthesized from 4 Daily Routines")

    # Get today's signals and findings from routines
    all_signals = get_all_signals()
    all_findings = get_all_findings()

    # Flexible date matching - handle various timestamp formats
    todays_signals = [s for s in all_signals if (
        str(s.get('date_recorded', ''))[:10] == today_str or
        str(s.get('date_recorded', '')).startswith(today_str)
    )]
    todays_findings = [f for f in all_findings if (
        str(f.get('date_discovered', ''))[:10] == today_str or
        str(f.get('date_discovered', '')).startswith(today_str)
    )]

    # Display routine-collected data
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Today's Signals", len(todays_signals))
    with col2:
        st.metric("Today's Findings", len(todays_findings))
    with col3:
        st.metric("Mechanisms Activated", len(set(f['mechanism'] for f in todays_findings)) if todays_findings else 0)
    with col4:
        st.metric("Total in System", len(all_signals))

    if todays_signals:
        with st.expander("[CHART] Today's Signals by Source", expanded=False):
            by_source = {}
            for s in todays_signals:
                src = s['source']
                if src not in by_source:
                    by_source[src] = []
                by_source[src].append(s)

            for source, signals in sorted(by_source.items()):
                st.markdown(f"**{source}** ({len(signals)} signals)")
                for signal in signals:
                    severity_color = {'critical': '[CRITICAL]', 'serious': '[WARNING]', 'warning': '[CAUTION]'}.get(signal['severity'], '[NEUTRAL]')
                    st.caption(f"{severity_color} {signal['domain']}: {signal['description'][:100]}...")

    if todays_findings:
        with st.expander("[ANALYSIS] Today's Research Findings by Mechanism", expanded=False):
            by_mech = {}
            for f in todays_findings:
                mech = f['mechanism']
                if mech not in by_mech:
                    by_mech[mech] = []
                by_mech[mech].append(f)

            for mech, findings_list in sorted(by_mech.items()):
                st.markdown(f"**{mech}** ({len(findings_list)} findings)")
                for finding in findings_list:
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.caption(finding['finding_text'][:150])
                    with col2:
                        st.metric("Confidence", f"{finding['confidence_level']:.0%}", label_visibility="collapsed")

    st.divider()

    # ============================================
    # SECTION 2: MANUAL CAPTURE FROM CHAT/SESSIONS
    # ============================================
    st.subheader("[WRITE] Add Finding from This Session")
    st.caption("Capture theoretical advances, methodological insights, or key realizations from your work")

    with st.expander("[DOCUMENT] Quick Capture Form", expanded=False):
        col1, col2 = st.columns([2, 1])

        with col1:
            new_finding = st.text_area(
                "Theoretical Advance or Key Finding",
                placeholder="E.g., Goal-driven architecture eliminates keyword brittleness and auto-adapts to scope changes",
                height=80,
                key="new_finding"
            )

        with col2:
            finding_type = st.selectbox(
                "Type",
                ["Theoretical Advance", "Methodological Insight", "System Discovery"],
                key="finding_type"
            )

        new_insight = st.text_area(
            "Methodological Insight (optional)",
            placeholder="E.g., Four-routine pipeline ensures multi-source convergence before signal elevation",
            height=60,
            key="new_insight"
        )

        if st.button("[SAVE] Save Finding", type="primary"):
            if new_finding.strip():
                # Load existing daily findings
                findings_data = get_daily_findings(today_str)

                if findings_data:
                    # Update existing entry
                    existing_advances = json.loads(findings_data['theoretical_advances'] or '[]')
                    existing_insights = json.loads(findings_data['methodological_insights'] or '[]')
                    existing_findings = json.loads(findings_data['findings'] or '[]')
                else:
                    existing_advances = []
                    existing_insights = []
                    existing_findings = []

                # Add new entries
                existing_advances.append(f"[{finding_type}] {new_finding}")
                if new_insight.strip():
                    existing_insights.append(new_insight)

                # Save to database
                from cascade_db import add_or_update_daily_findings
                overview = f"Today's synthesis: {len(todays_signals)} signals, {len(todays_findings)} findings, {len(existing_advances)} manual advances"
                add_or_update_daily_findings(
                    today_str,
                    overview,
                    json.dumps(existing_findings),
                    json.dumps(existing_insights),
                    json.dumps(existing_advances)
                )

                st.success("Finding saved! Reloading...")
                st.rerun()
            else:
                st.error("Please enter a finding")

    st.divider()

    # ============================================
    # SECTION 3: TODAY'S DAILY FINDINGS SUMMARY
    # ============================================
    findings_data = get_daily_findings(today_str)

    if findings_data:
        st.subheader("[LIST] Today's Complete Summary")

        # Overview
        if findings_data['overview']:
            st.markdown(f"**Overview**: {findings_data['overview']}")

        # Theoretical Advances
        if findings_data['theoretical_advances']:
            advances_list = json.loads(findings_data['theoretical_advances'])
            if advances_list:
                st.subheader("[MIND] Theoretical Advances")
                for advance in advances_list:
                    st.markdown(f'<div class="highlight-recent">• <strong>{advance}</strong></div>', unsafe_allow_html=True)

        # Methodological Insights
        if findings_data['methodological_insights']:
            insights_list = json.loads(findings_data['methodological_insights'])
            if insights_list:
                st.subheader("[CONFIG] Methodological Insights")
                for insight in insights_list:
                    st.markdown(f"• {insight}")

        st.caption(f"[DOCUMENT] Last updated: {findings_data['last_updated']}")
    else:
        if not todays_signals and not todays_findings:
            st.info("No signals or findings matched today's date. Routines will populate this when they run.")

            # Fallback: Show recent signals if date matching failed
            if all_signals:
                st.divider()
                st.subheader("[CHART] Recent Signals (Last 20) — Debug Fallback")
                st.caption("Showing recent data in case date format mismatched")

                recent_signals = all_signals[:20]
                for signal in recent_signals:
                    severity_color = {'critical': '[CRITICAL]', 'serious': '[WARNING]', 'warning': '[CAUTION]'}.get(signal.get('severity'), '[NEUTRAL]')
                    date_recorded = signal.get('date_recorded', 'unknown')
                    st.caption(f"{severity_color} [{date_recorded}] {signal.get('domain', 'Unknown')}: {signal.get('description', '')[:100]}...")

                st.caption("If you see Gmail results above, the date format may need adjustment. Check the timestamp format in the database.")

# ============================================
# 3. AMPLITUDE (formerly 4)
# ============================================
def section_amplitude():
    st.header("[CRITICAL] Amplitude Watch Log")

    st.markdown("""
    **Tracks whether individual cascade mechanisms are escalating in scale, severity, or impact.**

    Complements the PC Map (which documents mechanism presence) by monitoring mechanism **intensification**.
    Distinguishes between mechanisms that are simply active vs. mechanisms that are actively escalating.
    """)

    st.divider()

    # Get all amplitude watch entries
    amp_entries = get_amplitude_watch()

    if amp_entries:
        # Create summary metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            active = [e for e in amp_entries if e['status'] in ['ACCELERATING', 'STRUCTURAL']]
            st.metric("Active Escalations", len(active))

        with col2:
            avg_amp = sum(e['current_amplitude'] or 0 for e in amp_entries) / len(amp_entries) if amp_entries else 0
            st.metric("Average Amplitude", f"{avg_amp:.1f}")

        with col3:
            at_risk = [e for e in amp_entries if (e['current_amplitude'] or 0) > (e['risk_threshold'] or 100) * 0.7]
            st.metric("At-Risk Nodes", len(at_risk))

        with col4:
            high_conf = [e for e in amp_entries if e['confidence'] in ['HIGH', 'VERY HIGH']]
            st.metric("High Confidence", len(high_conf))

        st.divider()

        # Amplitude visualization
        st.subheader("[UP] Current Amplitude Levels by Status")

        viz_data = []
        for e in amp_entries:
            if e['current_amplitude'] is not None:
                viz_data.append({
                    'Node': f"Node {e['node_id']}",
                    'Mechanism': e['node_name'],
                    'Current': e['current_amplitude'],
                    'Risk Threshold': e['risk_threshold'],
                    'Status': e['status']
                })

        if viz_data:
            viz_df = pd.DataFrame(viz_data)
            fig = px.bar(viz_df, x='Mechanism', y='Current',
                        color='Status',
                        color_discrete_map={
                            'ACCELERATING': '#d03b3b',
                            'STRUCTURAL': '#fab219',
                            'EMERGING': '#ec835a',
                            'MODERATE': '#199e70',
                            'MONITORING': '#666666'
                        },
                        title="Cascade Node Amplitude (Escalation Magnitude)")
            fig.update_layout(height=400, xaxis_tickangle=-45)
            st.plotly_chart(fig)

        st.divider()

        # Detailed watch log entries
        st.subheader("[SEARCH] Detailed Amplitude Watch Entries")

        # Group by status for better organization
        statuses = ['ACCELERATING', 'STRUCTURAL', 'EMERGING', 'MODERATE', 'MONITORING']

        for status in statuses:
            status_entries = [e for e in amp_entries if e['status'] == status]

            if status_entries:
                with st.expander(f"**{status}** ({len(status_entries)} mechanisms)", expanded=(status in ['ACCELERATING', 'STRUCTURAL'])):
                    for entry in status_entries:
                        col1, col2 = st.columns([2, 3])

                        with col1:
                            st.markdown(f"**Node {entry['node_id']}: {entry['node_name']}**")
                            st.metric("Current Amplitude", f"{entry['current_amplitude']:.0f}" if entry['current_amplitude'] else "—")
                            st.metric("Risk Threshold", f"{entry['risk_threshold']:.0f}" if entry['risk_threshold'] else "—")

                            # Progress bar showing amplitude vs risk threshold
                            if entry['current_amplitude'] and entry['risk_threshold']:
                                pct = min(100, int(entry['current_amplitude'] / entry['risk_threshold'] * 100))
                                st.progress(pct / 100, text=f"{pct}% of risk threshold")

                        with col2:
                            st.markdown(f"**Escalation**: {entry['escalation_rate']}")
                            st.markdown(f"**Confidence**: {entry['confidence']}")
                            st.markdown(f"**Measurement Basis**: {entry['measurement_basis']}")
                            st.markdown(f"**Breakpoint**: {entry['breakpoint']}")
                            if entry['evidence']:
                                st.markdown(f"**Evidence**: {entry['evidence']}")

        st.divider()

        # Amplitude trends over time
        st.subheader("Reference Point Amplitude Trend")
        ref_points = get_reference_points()

        if ref_points:
            df_ref = pd.DataFrame(ref_points)
            df_ref['date_recorded'] = pd.to_datetime(df_ref['date_recorded'])
            df_ref = df_ref[df_ref['metric_name'] == 'Amplitude'].sort_values('date_recorded')

            if not df_ref.empty:
                fig = px.line(df_ref, x='date_recorded', y='value',
                             markers=True, title="Amplitude Trend")
                fig.update_xaxes(title_text="Date")
                fig.update_yaxes(title_text="Amplitude Value")
                st.plotly_chart(fig)
    else:
        st.info("No amplitude data available yet")

# ============================================
# 5. CASCADING NODES VISUALIZING
# ============================================
def section_cascading_nodes():
    st.header("[LINK] Cascading Nodes Visualizing")

    st.subheader("CASCADE Sequences")

    sequences = get_cascade_sequences()

    if sequences:
        seq_df = pd.DataFrame(sequences)
        seq_df = seq_df[['cascade_id', 'name', 'node_sequence', 'confidence']]
        seq_df.columns = ['ID', 'Name', 'Node Chain', 'Confidence']
        st.dataframe(seq_df, width='stretch', hide_index=True)

        st.divider()

        st.subheader("Node Activation Matrix")

        nodes = get_all_nodes()

        # Create activation matrix
        node_grid = []
        for node in nodes:
            signals_for_node = get_node_signals(node['node_id'])
            node_grid.append({
                'Node': f"Node {node['node_id']}",
                'Mechanism': node['name'],
                'Status': node['status'].upper(),
                'Signals': len(signals_for_node),
                'Amplitude': node['amplitude'],
                'Frequency': node['frequency']
            })

        if node_grid:
            grid_df = pd.DataFrame(node_grid)
            st.dataframe(grid_df, width='stretch', hide_index=True)

            # Visualization
            st.subheader("Node Activity Scatter")

            # Color by Status instead of Amplitude (Amplitude already on x-axis)
            status_colors = {
                'ACTIVE': '#d03b3b',      # Critical red
                'MONITORING': '#3987e5',  # Blue
                'ACCELERATING': '#ec835a' # Serious orange
            }

            fig = px.scatter(grid_df, x='Amplitude', y='Frequency',
                           size='Signals', hover_name='Mechanism',
                           color='Status',
                           color_discrete_map=status_colors,
                           title="Node Activation Landscape")
            fig.update_layout(height=450)
            st.plotly_chart(fig)
    else:
        st.info("No CASCADE sequences recorded yet")

# ============================================
# 6. SYSTEMATIC UNDERESTIMATION
# ============================================
def section_systematic_underestimation():
    st.header("[WARNING] Systematic Underestimation")

    st.subheader("Definition")
    st.markdown("""
    A structural pattern where institutions, models, and frameworks systematically underestimate
    climate crisis severity, speed, and interconnectedness—not from bad data, but because
    measurement and policy instruments are calibrated for a world that no longer exists.
    """)

    # Summary metrics
    summary = get_underestimation_summary()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Findings", summary['total_findings'])
    with col2:
        st.metric("Critical Gaps", summary['critical'])
    with col3:
        st.metric("Domains Affected", summary['unique_domains'])
    with col4:
        st.metric("Categories", summary['unique_categories'])

    st.divider()

    # Filter by domain
    domains = get_underestimation_domains()
    if domains:
        selected_domain = st.selectbox("Filter by Domain", ["All"] + domains)

        if selected_domain == "All":
            findings = get_all_underestimations()
        else:
            findings = get_all_underestimations(domain=selected_domain)

        if findings:
            # Organize by severity
            critical_findings = [f for f in findings if f['severity'] == 'critical']
            serious_findings = [f for f in findings if f['severity'] == 'serious']
            moderate_findings = [f for f in findings if f['severity'] == 'moderate']

            # Display critical findings
            if critical_findings:
                st.subheader("[CRITICAL] Critical Underestimations")
                for finding in critical_findings:
                    with st.container(border=True):
                        col1, col2 = st.columns([0.85, 0.15])
                        with col1:
                            st.markdown(f"**{finding['domain'].title()}** — {finding['category'].title()}")
                            st.markdown(finding['finding_text'])
                            if finding['underestimation_factor']:
                                st.caption(f"**Underestimation Factor:** {finding['underestimation_factor']}")
                            if finding['actual_vs_predicted']:
                                st.caption(f"**Actual vs Predicted:** {finding['actual_vs_predicted']}")
                            if finding['evidence_text']:
                                st.caption(f"**Evidence:** {finding['evidence_text']}")
                            st.caption(f"_Source: {finding['source']} | {finding['date_recorded'][:10]}_")
                        with col2:
                            st.markdown("<span style='color: #d03b3b; font-weight: 600; font-size: 12px;'>CRITICAL</span>", unsafe_allow_html=True)

            # Display serious findings
            if serious_findings:
                st.subheader("[WARNING] Serious Underestimations")
                for finding in serious_findings:
                    with st.container(border=True):
                        col1, col2 = st.columns([0.85, 0.15])
                        with col1:
                            st.markdown(f"**{finding['domain'].title()}** — {finding['category'].title()}")
                            st.markdown(finding['finding_text'])
                            if finding['underestimation_factor']:
                                st.caption(f"**Underestimation Factor:** {finding['underestimation_factor']}")
                            if finding['actual_vs_predicted']:
                                st.caption(f"**Actual vs Predicted:** {finding['actual_vs_predicted']}")
                            if finding['evidence_text']:
                                st.caption(f"**Evidence:** {finding['evidence_text']}")
                            st.caption(f"_Source: {finding['source']} | {finding['date_recorded'][:10]}_")
                        with col2:
                            st.markdown("<span style='color: #ec835a; font-weight: 600; font-size: 12px;'>SERIOUS</span>", unsafe_allow_html=True)

            # Display moderate findings
            if moderate_findings:
                with st.expander(f"[CAUTION] Moderate Underestimations ({len(moderate_findings)})"):
                    for finding in moderate_findings:
                        with st.container(border=True):
                            st.markdown(f"**{finding['domain'].title()}** — {finding['category'].title()}")
                            st.markdown(finding['finding_text'])
                            if finding['underestimation_factor']:
                                st.caption(f"**Underestimation Factor:** {finding['underestimation_factor']}")
                            if finding['evidence_text']:
                                st.caption(f"**Evidence:** {finding['evidence_text']}")
                            st.caption(f"_Source: {finding['source']} | {finding['date_recorded'][:10]}_")

        else:
            st.info("No underestimation findings in this domain yet.")
    else:
        st.info("No systematic underestimation findings recorded yet.")

# ============================================
# 7. GRANULARITY
# ============================================
def section_granularity():
    st.header("[ANALYSIS] Granularity")

    st.subheader("Signal Detail Breakdown")

    signals = get_all_signals()

    if signals:
        signals_df = pd.DataFrame(signals)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Signals", len(signals_df))
            st.metric("Unique Domains", signals_df['domain'].nunique())

        with col2:
            st.metric("Unique Severities", signals_df['severity'].nunique())
            st.metric("Unique Sources", signals_df['source'].nunique())

        with col3:
            active = signals_df[signals_df['status'] == 'active']
            st.metric("Active Signals", len(active))

        st.divider()

        st.subheader("Signals by Domain")

        domain_counts = signals_df['domain'].value_counts()
        fig = px.bar(x=domain_counts.index, y=domain_counts.values,
                    labels={'x': 'Domain', 'y': 'Signal Count'},
                    title="Signal Distribution by Domain")
        st.plotly_chart(fig)

        st.divider()

        st.subheader("Signals by Severity")

        severity_counts = signals_df['severity'].value_counts()
        fig = px.pie(values=severity_counts.values, names=severity_counts.index,
                    title="Severity Distribution")
        st.plotly_chart(fig)

        st.divider()

        st.subheader("All Signals (Detailed View)")
        st.dataframe(signals_df, width='stretch', hide_index=True)

    else:
        st.info("No signals recorded yet")

# ============================================
# 8. APPENDIX
# ============================================
def section_appendix():
    st.header("[LIBRARY] Appendix")

    st.subheader("Baseline Return Failures")

    baseline_failures = get_baseline_failures()

    if baseline_failures:
        bf_df = pd.DataFrame(baseline_failures)
        bf_summary = bf_df.groupby('geography').agg({'baseline_shift_percent': 'first'}).reset_index()
        bf_summary.columns = ['Geography/Sector', 'Baseline Shift %']

        fig = px.bar(bf_summary, x='Geography/Sector', y='Baseline Shift %',
                    title="Baseline Return Failure by Geography")
        fig.update_traces(marker=dict(color='#3987e5'))
        st.plotly_chart(fig)

        st.divider()

        st.subheader("Baseline Failure Details")
        st.dataframe(bf_df, width='stretch', hide_index=True)
    else:
        st.info("No baseline failure data recorded yet")

    st.divider()

    st.subheader("Data Schema")
    st.markdown("""
    **Project Cascade Database contains:**
    - **Cascade Nodes**: 13 primary mechanisms of system failure
    - **Signals**: Discrete observations of mechanism activation
    - **CASCADE Sequences**: Documented causal chains between nodes
    - **Reference Points**: Amplitude, Frequency, Interconnectedness, Underestimation
    - **Baseline Failures**: Geographic/sectoral baseline return patterns
    - **Daily Summaries**: Timestamped assessments and findings
    """)

# ============================================
# 9. SYSTEM MECHANISM TRACKER
# ============================================
def section_system_mechanism_tracker():
    st.header("[ANALYSIS] System Mechanism Tracker")
    st.markdown("Distributed Adaptation Network & Baseline Return Failure Analysis")

    # Get data
    metrics = get_metrics_summary()
    nodes_by_activity = get_nodes_by_activity()
    cascades_with_signals = get_cascade_sequences_with_signals()
    hotspots = get_geographic_hotspots()
    amplitude_watch = get_amplitude_watch()

    # KEY METRICS ROW
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Signals", metrics['total_signals'], "+20 since Aug 17")
    with col2:
        active_count = len([n for n in nodes_by_activity if n['status'] == 'active'])
        st.metric("Active Mechanisms", f"{active_count}/13", "Nodes 3,4,5,6,7,11,13")
    with col3:
        st.metric("System Robustness", "−12%", "↓ −7% degradation")
    with col4:
        st.metric("CASCADE Sequences", metrics['cascade_sequences'], "5+ simultaneous")

    st.divider()

    # NODE ACTIVATION STATUS
    st.subheader("Node Activation Status — Amplitude & Frequency")

    # Create node cards with dynamic coloring
    node_map = {
        3: ("Institutional Suppression", "#d03b3b"),
        4: ("Rate of Change", "#d03b3b"),
        5: ("Thresholds Becoming Floors", "#d03b3b"),
        6: ("Measurement Erosion", "#ec835a"),
        7: ("Economic Depletion", "#d03b3b"),
        11: ("Infrastructure Lock-In", "#ec835a"),
        13: ("Change/Adaptation Lag", "#d03b3b"),
    }

    cols = st.columns(7)
    for idx, (node_id, (name, color)) in enumerate(node_map.items()):
        with cols[idx]:
            # Get node status from database
            node_data = next((n for n in nodes_by_activity if n['node_id'] == node_id), None)
            amplitude = f"{node_data['amplitude']:.1f}" if node_data else "—"

            # Find corresponding amplitude watch entry
            amp_watch = next((a for a in amplitude_watch if a['node_id'] == node_id), None)
            status = amp_watch['status'] if amp_watch else 'MONITORING'

            st.markdown(f"""
            <div style='background: #252423; border-left: 4px solid {color}; border-radius: 6px; padding: 16px; text-align: center;'>
                <div style='font-size: 12px; font-weight: 600; color: #c3c2b7; margin-bottom: 8px;'>Node {node_id}</div>
                <div style='font-size: 20px; font-weight: 600; color: #ffffff; margin-bottom: 4px;'>{status}</div>
                <div style='font-size: 11px; color: #8a8984;'>{name}</div>
            </div>
            """, unsafe_allow_html=True)

    st.divider()

    # CHARTS SECTION
    st.subheader("Analysis & Trends")

    chart_col1, chart_col2 = st.columns(2)

    # Signal Distribution Chart
    with chart_col1:
        st.markdown("**Signal Distribution Across Nodes**")
        nodes_by_act = sorted(nodes_by_activity, key=lambda x: x['signal_count'], reverse=True)[:7]

        signal_data = {
            'Node': [f"Node {n['node_id']}" for n in nodes_by_act],
            'Signals': [n['signal_count'] for n in nodes_by_act]
        }

        fig = px.bar(
            signal_data,
            x='Node',
            y='Signals',
            labels={'Signals': 'Signal Count'},
        )
        fig.update_traces(marker=dict(color='#3987e5'))
        fig.update_layout(
            height=300,
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#c3c2b7'),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='#383835'),
            margin=dict(l=0, r=0, t=0, b=0)
        )
        st.plotly_chart(fig)

    # Reference Points Trend
    with chart_col2:
        st.markdown("**Reference Points Escalation**")

        ref_trend = {
            'Date': ['Aug 14', 'Aug 15', 'Aug 16', 'Aug 17', 'Aug 18'],
            'Amplitude': [28, 28, 28, 28, 34],
            'Frequency': [36, 36, 36, 36, 44],
            'Interconnectedness': [26, 26, 26, 26, 33],
        }

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=ref_trend['Date'], y=ref_trend['Amplitude'],
                                name='Amplitude', line=dict(color='#3987e5', width=2)))
        fig.add_trace(go.Scatter(x=ref_trend['Date'], y=ref_trend['Frequency'],
                                name='Frequency', line=dict(color='#d95926', width=2)))
        fig.add_trace(go.Scatter(x=ref_trend['Date'], y=ref_trend['Interconnectedness'],
                                name='Interconnectedness', line=dict(color='#199e70', width=2)))

        fig.update_layout(
            height=300,
            hovermode='x unified',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#c3c2b7'),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='#383835'),
            legend=dict(x=0, y=1, bgcolor='rgba(0,0,0,0)', bordercolor='rgba(0,0,0,0)'),
            margin=dict(l=0, r=0, t=0, b=0)
        )
        st.plotly_chart(fig)

    robustness_col, baseline_col = st.columns(2)

    # System Robustness
    with robustness_col:
        st.markdown("**System Robustness Degradation**")

        robustness_data = {
            'Date': ['Aug 14', 'Aug 15', 'Aug 16', 'Aug 17', 'Aug 18'],
            'Robustness': [-2, -3, -4, -5, -12],
        }

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=robustness_data['Date'],
            y=robustness_data['Robustness'],
            fill='tozeroy',
            line=dict(color='#d03b3b', width=3),
            fillcolor='rgba(208, 59, 59, 0.1)',
            name='System Robustness'
        ))

        fig.update_layout(
            height=300,
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#c3c2b7'),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='#383835', ticksuffix='%'),
            margin=dict(l=0, r=0, t=0, b=0)
        )
        st.plotly_chart(fig)

    # Baseline Return Failures
    with baseline_col:
        st.markdown("**Baseline Return Failures — Geographic Expansion**")

        baseline_data = {
            'Region': ['Colorado River', 'Great Lakes', 'U.S. Agriculture', 'SE Asia', 'Sub-Saharan', 'Louisiana'],
            'Impact': ['−33%', '−18%', '−6M acres', '−27%', '−31%', '−12 insurers'],
            'Sector': ['Water', 'Water', 'Crop', 'Agr+Water', 'Agr+Water', 'Insurance']
        }

        for idx, region in enumerate(baseline_data['Region']):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.caption(f"**{region}** — {baseline_data['Sector'][idx]}")
            with col2:
                st.caption(f"_{baseline_data['Impact'][idx]}_")

    st.divider()

    # CASCADE SEQUENCES
    st.subheader("Active CASCADE Sequences (5+ Simultaneous)")

    cascade_sequences = [
        ("CASCADE 4", "Node 7→6→10→3 (Economic Depletion Sequence)", "HIGH"),
        ("CASCADE 9", "Node 13→3 (Change Immunity Lock-In)", "HIGH"),
        ("CASCADE 10", "Node 3→7 (Institutional Suppression → Economic Depletion)", "HIGH"),
        ("CASCADE 11", "Node 3→6 (Institutional Suppression → Measurement Erosion)", "HIGH"),
        ("CASCADE 12", "Node 7→13 (Economic Depletion → Adaptation Lag)", "HIGH"),
    ]

    for name, nodes, conf in cascade_sequences:
        col1, col2, col3 = st.columns([1, 3, 1])
        with col1:
            st.markdown(f"**{name}**")
        with col2:
            st.caption(nodes)
        with col3:
            st.markdown(f"<span style='background: #2f2e2c; padding: 4px 8px; border-radius: 4px; font-size: 11px; color: #d03b3b; font-weight: 600;'>{conf}</span>", unsafe_allow_html=True)

    st.divider()

    # KEY REFERENCE POINTS
    st.subheader("Key Reference Points — Amplitude, Frequency, Interconnectedness")

    ref_col1, ref_col2, ref_col3, ref_col4 = st.columns(4)

    ref_points = [
        ("Amplitude", 34, "+21%"),
        ("Frequency", 44, "+22%"),
        ("Interconnectedness", 33, "+27%"),
        ("Systematic Underestimation", 28, "+65%"),
    ]

    cols = [ref_col1, ref_col2, ref_col3, ref_col4]
    for idx, (label, value, delta) in enumerate(ref_points):
        with cols[idx]:
            st.markdown(f"""
            <div style='background: #2f2e2c; border-radius: 6px; padding: 12px; text-align: center;'>
                <div style='font-size: 11px; font-weight: 600; text-transform: uppercase; color: #c3c2b7; margin-bottom: 4px;'>{label}</div>
                <div style='font-size: 28px; font-weight: 600; color: #ffffff;'>{value}</div>
                <div style='font-size: 12px; color: #d03b3b; font-weight: 600;'>{delta} ↑</div>
            </div>
            """, unsafe_allow_html=True)

    st.divider()
    st.caption("Project Cascade — Distributed Adaptation Network & Baseline Return Failure Analysis Integrated | 17 Tracking Domains | Monthly Assessment Cycle")

# ============================================
# 10. PROJECT GOALS
# ============================================
def section_project_goals():
    st.header("[TARGET] Project Goals & Objectives")

    # Primary mission statement
    st.markdown("""
    ### Mission Statement
    Track and visualize forces and mechanisms that contribute to cascading failure and/or critical capacity
    thresholds across earth systems and human institutions.
    """)

    st.divider()

    # Framework section (from former Mission and Goals page)
    st.subheader("Framework")
    st.markdown("""
    **Project Cascade** tracks 13 mechanisms documenting how constrained systems fail sequentially.

    **13 Cascade Nodes:**
    1. Water Bankruptcy
    2. Regulatory Capture
    3. Institutional Suppression
    4. Rate of Change
    5. Thresholds Becoming Floors
    6. Measurement Capacity Erosion
    7. Economic Depletion
    8. Infrastructure Brittleness
    9. Scenario Planning Collapse
    10. Coordination Cascade Failure
    11. Infrastructure Built for Still Climate
    12. Adaptation Exhaustion
    13. Change/Adaptation Lag
    """)

    st.divider()

    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["Active Goals", "Retired Goals", "Add New Goal"])

    all_goals = get_all_goals()
    active_goals = [g for g in all_goals if g['status'] == 'active']
    retired_goals = [g for g in all_goals if g['status'] == 'retired']

    # TAB 1: ACTIVE GOALS
    with tab1:
        st.subheader(f"Active Goals ({len(active_goals)})")

        if active_goals:
            for idx, goal in enumerate(active_goals):
                col1, col2, col3 = st.columns([0.8, 0.1, 0.1])

                with col1:
                    st.markdown(f"""
                    <div style='background: #252423; border-left: 4px solid #199e70; border-radius: 6px; padding: 16px; margin: 8px 0;'>
                        <div style='font-size: 14px; color: #ffffff;'>{goal['goal_text']}</div>
                        <div style='font-size: 11px; color: #8a8984; margin-top: 8px;'>
                            Created: {goal['created_date'][:10]} | Category: {goal['category']}
                        </div>
                        {f"<div style='font-size: 11px; color: #c3c2b7; margin-top: 4px;'>Last amended: {goal['amended_date'][:10]}</div>" if goal['amended_date'] else ""}
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    if st.button("[EDIT]", key=f"edit_{goal['goal_id']}", help="Edit goal"):
                        st.session_state.edit_goal_id = goal['goal_id']

                with col3:
                    if st.button("[DELETE]", key=f"retire_{goal['goal_id']}", help="Retire goal"):
                        retire_goal(goal['goal_id'], notes=f"Retired on {datetime.now().strftime('%Y-%m-%d')}")
                        st.rerun()

            # Edit mode
            if 'edit_goal_id' in st.session_state:
                goal_to_edit = next((g for g in active_goals if g['goal_id'] == st.session_state.edit_goal_id), None)
                if goal_to_edit:
                    st.divider()
                    st.subheader("Edit Goal")

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

                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("[SAVE] Save Changes"):
                            update_goal(st.session_state.edit_goal_id, edited_text, edited_category)
                            del st.session_state.edit_goal_id
                            st.success("Goal updated!")
                            st.rerun()

                    with col2:
                        if st.button("[FAILED] Cancel"):
                            del st.session_state.edit_goal_id
                            st.rerun()
        else:
            st.info("No active goals yet. Add one using the 'Add New Goal' tab.")

    # TAB 2: RETIRED GOALS
    with tab2:
        st.subheader(f"Retired Goals ({len(retired_goals)})")

        if retired_goals:
            for goal in retired_goals:
                col1, col2 = st.columns([0.9, 0.1])

                with col1:
                    st.markdown(f"""
                    <div style='background: #252423; border-left: 4px solid #8a8984; border-radius: 6px; padding: 16px; margin: 8px 0; opacity: 0.7;'>
                        <div style='font-size: 14px; color: #c3c2b7;'>{goal['goal_text']}</div>
                        <div style='font-size: 11px; color: #8a8984; margin-top: 8px;'>
                            Retired: {goal['retired_date'][:10]} | {goal['notes']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    if st.button("[REACTIVATE]", key=f"reactivate_{goal['goal_id']}", help="Reactivate goal"):
                        activate_goal(goal['goal_id'])
                        st.success("Goal reactivated!")
                        st.rerun()
        else:
            st.info("No retired goals.")

    # TAB 3: ADD NEW GOAL
    with tab3:
        st.subheader("Add New Goal")

        new_goal_text = st.text_area(
            "Goal Description",
            placeholder="Enter a new project goal...",
            height=100
        )

        new_category = st.selectbox(
            "Category",
            ["primary", "secondary", "supporting", "monitoring"],
            key="new_goal_category"
        )

        if st.button("[ADD] Add Goal", type="primary"):
            if new_goal_text.strip():
                add_goal(new_goal_text, new_category)
                st.success("Goal added successfully!")
                st.rerun()
            else:
                st.error("Please enter a goal description.")

    st.divider()

    # Summary statistics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Active Goals", len(active_goals))
    with col2:
        st.metric("Retired Goals", len(retired_goals))
    with col3:
        st.metric("Total Goals", len(all_goals))

# ============================================
# 9. RESEARCH FINDINGS
# ============================================
def section_findings():
    st.header("[ANALYSIS] Research Findings — Mechanisms and Evidence")

    # HEADLINE: Core finding first
    st.markdown("**Global recovery capacity is severely constrained. The intervention window is closing.**")
    st.markdown("---")

    # Project summary - global focus, under 100 words
    st.subheader("[REFERENCE] Synthesis & Key Insights")
    st.markdown("**Global Cascade Crisis**: Eight interconnected failure mechanisms are destabilizing planetary systems. Critical thresholds crossed:")
    st.markdown("&nbsp;&nbsp;&nbsp;&nbsp;• **Water Scarcity** — Lake Powell/Mead at record lows; regional aquifers depleting")
    st.markdown("&nbsp;&nbsp;&nbsp;&nbsp;• **Energy Infrastructure Vulnerability** — 128-week transformer lead times; 75% of equipment past service life")
    st.markdown("&nbsp;&nbsp;&nbsp;&nbsp;• **Institutional Response Lag** — Policy windows closing faster than adaptation capacity")
    st.markdown("&nbsp;&nbsp;&nbsp;&nbsp;• **Feedback Amplification** — Supply shocks triggering panic-buying cascades")
    st.markdown("&nbsp;&nbsp;&nbsp;&nbsp;• **Coordination Failure** — Nine grid nodes could blackout continents")
    st.markdown("&nbsp;&nbsp;&nbsp;&nbsp;• **Economic Depletion** — Cascading responses exhausting capital reserves")
    st.markdown("&nbsp;&nbsp;&nbsp;&nbsp;• **Measurement Blindness** — No comprehensive system visibility; blind spots widening")
    st.markdown("&nbsp;&nbsp;&nbsp;&nbsp;• **Bifurcation Risk** — Systems approaching irreversible transitions")
    st.markdown("Global recovery capacity is severely constrained. The intervention window is closing.")
    st.markdown("---")

    # Regional summaries
    st.subheader("[WORLD] Regional Vulnerability Profiles")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### North America")
        st.write("""
**Critical Vulnerabilities**: Aging power grid (average transformer age 38+ years); water system stress (Colorado River Basin at crisis); supply chain brittleness (single-point failures in electrical steel production).

**Cascading Risk**: Grid collapse → water treatment failure → social breakdown within 72 hours.

**Institutional Capacity**: Moderate; fragmented response (federal/state/utility levels); recovery timelines measured in years.
        """)

    with col2:
        st.markdown("#### Europe")
        st.write("""
**Critical Vulnerabilities**: Energy dependency on unstable supplies; aging infrastructure post-war recovery; coordination fragmentation (27 EU members, multiple grids).

**Cascading Risk**: Energy supply shock → economic collapse → migration cascade → internal instability.

**Institutional Capacity**: High coordination intent; constrained by political fragmentation and capital limits.
        """)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Asia-Pacific")
        st.write("""
**Critical Vulnerabilities**: Rapid urbanization outpacing infrastructure; water stress (Mekong, Brahmaputra); monsoon dependence; extreme supply chain concentration.

**Cascading Risk**: Monsoon failure → crop failure → food system collapse → mass migration.

**Institutional Capacity**: Variable (China high, others lower); coordination across nations minimal.
        """)

    with col2:
        st.markdown("#### Sub-Saharan Africa")
        st.write("""
**Critical Vulnerabilities**: Infrastructure underdeveloped; water scarcity accelerating; institutional capacity lowest globally; highest climate exposure.

**Cascading Risk**: Drought → pastoralist collapse → conflict → displacement → pandemic risk.

**Institutional Capacity**: Lowest; dependent on external aid; recovery windows measured in decades if at all.
        """)

    st.markdown("---")

    # Dynamic finding synthesis - exclude today's findings (shown in Today's Progress)
    from datetime import date as date_class
    today_str = date_class.today().isoformat()

    all_findings = get_all_findings()
    # Filter to exclude today's findings - show project arc, not daily news
    project_findings = [f for f in all_findings if f['date_discovered'] != today_str]

    if project_findings:
        st.subheader("[REFERENCE] Synthesis & Key Insights")

        # Organize findings by mechanism for narrative
        by_mechanism = {}
        for finding in project_findings:
            mech = finding['mechanism']
            if mech not in by_mechanism:
                by_mechanism[mech] = []
            by_mechanism[mech].append(finding)

        # Generate concise synthesis
        synthesis = []

        if 'Threshold Dynamics' in by_mechanism:
            count = len(by_mechanism['Threshold Dynamics'])
            synthesis.append(f"**Threshold Dynamics** ({count}): Critical inflection points crossed in energy, water, infrastructure.")

        if 'Institutional Lag' in by_mechanism:
            count = len(by_mechanism['Institutional Lag'])
            synthesis.append(f"**Institutional Lag** ({count}): Policy responses lag system acceleration; recovery timescales exceed intervention windows.")

        if 'Feedback Amplification' in by_mechanism:
            count = len(by_mechanism['Feedback Amplification'])
            synthesis.append(f"**Feedback Amplification** ({count}): Supply shocks trigger panic responses, extending disruption cascades.")

        if 'Coupling & Interdependence' in by_mechanism:
            count = len(by_mechanism['Coupling & Interdependence'])
            synthesis.append(f"**Coupling & Interdependence** ({count}): 9 substations can collapse entire grid; systemic fragility hidden by complexity.")

        infra_count = 0
        if 'Infrastructure Built for Still Climate' in by_mechanism:
            infra_count += len(by_mechanism['Infrastructure Built for Still Climate'])
        if 'Tipping Points & Bifurcation' in by_mechanism:
            infra_count += len(by_mechanism['Tipping Points & Bifurcation'])
        if infra_count > 0:
            synthesis.append(f"**Infrastructure & Bifurcation** ({infra_count}): Aging grid strained by AI load spikes; dual-use transformation underway.")

        blind_count = 0
        if 'Measurement & Uncertainty' in by_mechanism:
            blind_count += len(by_mechanism['Measurement & Uncertainty'])
        if 'Economic Depletion' in by_mechanism:
            blind_count += len(by_mechanism['Economic Depletion'])
        if blind_count > 0:
            synthesis.append(f"**Blind Spots & Resource Constraints** ({blind_count}): No comprehensive inventory; $2.5B+ replacement costs unsustainable.")

        # Display synthesis in a readable container
        synthesis_text = "\n\n".join(synthesis)
        st.markdown(f"""
        <div style="background-color: #1a1a19; padding: 16px; border-radius: 8px; border-left: 4px solid #3987e5;">
        {synthesis_text}
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

    # Summary metrics (project-wide, excluding today)
    project_summary = {
        'total_findings': len(project_findings) if project_findings else 0,
        'avg_confidence': sum([f['confidence_level'] for f in project_findings]) / len(project_findings) if project_findings else 0,
        'unique_mechanisms': len(set([f['mechanism'] for f in project_findings])) if project_findings else 0
    }

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Project Findings", project_summary['total_findings'])
    with col2:
        st.metric("Average Confidence", f"{project_summary['avg_confidence']:.2%}")
    with col3:
        st.metric("Mechanisms Covered", project_summary['unique_mechanisms'])

    st.markdown("---")

    # Mechanism breakdown
    st.subheader("[CHART] Findings by Mechanism")

    # Filter mechanisms data to exclude today's findings
    if project_findings:
        mech_summary = {}
        for f in project_findings:
            mech = f['mechanism']
            if mech not in mech_summary:
                mech_summary[mech] = {'count': 0, 'confidences': []}
            mech_summary[mech]['count'] += 1
            mech_summary[mech]['confidences'].append(f['confidence_level'])

        mechanisms_data = [
            {
                'mechanism': mech,
                'count': data['count'],
                'avg_confidence': sum(data['confidences']) / len(data['confidences'])
            }
            for mech, data in mech_summary.items()
        ]
    else:
        mechanisms_data = []

    if mechanisms_data:
        # Create mechanism distribution chart
        mech_df = pd.DataFrame(mechanisms_data)

        col1, col2 = st.columns(2)

        # Chart 1: Findings count by mechanism
        with col1:
            fig_count = px.bar(
                mech_df,
                x='mechanism',
                y='count',
                title='Number of Findings per Mechanism',
                labels={'count': 'Finding Count', 'mechanism': 'Mechanism'}
            )
            fig_count.update_traces(marker=dict(color='#3987e5'))
            fig_count.update_layout(
                showlegend=False,
                height=400,
                font=dict(size=11)
            )
            st.plotly_chart(fig_count)

        # Chart 2: Average confidence by mechanism
        with col2:
            fig_conf = px.bar(
                mech_df,
                x='mechanism',
                y='avg_confidence',
                title='Average Confidence Level by Mechanism',
                labels={'avg_confidence': 'Avg Confidence', 'mechanism': 'Mechanism'}
            )
            fig_conf.update_traces(marker=dict(color='#3987e5'))
            fig_conf.update_layout(
                showlegend=False,
                height=400,
                font=dict(size=11),
                yaxis=dict(tickformat='.0%')
            )
            st.plotly_chart(fig_conf)

    st.markdown("---")

    # Detailed findings by mechanism (project arc, excluding today)
    st.subheader("[LIST] Findings Details (Project to-Date)")

# ============================================
# 2. SYSTEM DYNAMICS
# ============================================
def section_system_dynamics():
    st.header("[WORLD] Global Critical Infrastructure Cascade Dynamics")

    st.markdown("""
    How failures in one critical system trigger cascades across regions and sectors.
    Different regions experience different cascade pathways depending on their economic
    structure, climate vulnerability, and infrastructure interdependencies.
    """)

    st.subheader("[LINK] Regional Cascade Pathways")

    st.markdown("""
    Critical infrastructure systems are tightly coupled globally. A failure in one region's
    system can trigger failures across multiple continents through trade, energy, food, and
    financial interdependencies.
    """)

    # Define regional cascades
    regional_cascades = {
        'North America': {
            'trigger': 'Electrical grid collapse (9 substations)',
            'pathway': 'Grid → Water treatment → Fuel delivery → Food distribution → Social breakdown',
            'timescale': '3-7 days to cascade',
            'global_impact': 'Food exports stop (Canada wheat, US corn) → global grain crisis'
        },
        'Europe': {
            'trigger': 'Energy shock (Russian supply cut)',
            'pathway': 'Energy → Heat/cooling failure → Economic collapse → Migration cascade',
            'timescale': '1-2 weeks to cascade',
            'global_impact': 'Fertilizer production stops → global agriculture crisis'
        },
        'Asia-Pacific': {
            'trigger': 'Monsoon failure or extreme weather',
            'pathway': 'Crop failure → Food crisis → Migration → Conflict → Regional instability',
            'timescale': '2-3 months to cascade',
            'global_impact': 'Grain shortages → global price spike; Mekong collapse → 60M+ displaced'
        },
        'Sub-Saharan Africa': {
            'trigger': 'Drought (water stress)',
            'pathway': 'Water → Pastoralist collapse → Conflict → Famine → Disease → Displacement',
            'timescale': '6-12 months to cascade',
            'global_impact': 'Regional instability → migration pressure on Europe/Middle East'
        }
    }

    for region, cascade in regional_cascades.items():
        with st.container():
            col1, col2 = st.columns([1, 2])
            with col1:
                st.markdown(f"**{region}**")
                st.caption(f"Timescale: {cascade['timescale']}")
            with col2:
                st.markdown(f"**Trigger:** {cascade['trigger']}")
                st.markdown(f"**Cascade:** {cascade['pathway']}")
                st.markdown(f"**Global Impact:** {cascade['global_impact']}")
            st.divider()

    st.divider()

    # SECTION 1: Global System Interdependencies
    st.subheader("[DATE] Timescale Variation by Region and System")

    st.markdown("""
    Different critical systems fail at different timescales. The cascade effect means that
    as one system fails, it triggers failures in others—but the timing varies by region and
    infrastructure type.
    """)

    timescale_comparison = {
        'System Failure': ['Electrical Grid', 'Water Treatment', 'Food Distribution', 'Semiconductor Supply', 'Agricultural System'],
        'North America': ['Minutes-Hours', 'Hours-Days', 'Days-Weeks', 'Weeks-Months', 'Months-Years'],
        'Europe': ['Hours-Days', 'Days-Weeks', 'Weeks-Months', 'Months-Years', 'Years'],
        'Asia-Pacific': ['Days-Weeks', 'Weeks-Months', 'Months', 'Months-Years', 'Years+'],
        'Sub-Saharan Africa': ['Weeks-Months', 'Months', 'Months-Years', 'Years', 'Years+'],
    }

    col1, col2, col3, col4, col5 = st.columns(5)

    cols = [col1, col2, col3, col4, col5]

    for idx, key in enumerate(timescale_comparison.keys()):
        with cols[idx]:
            st.markdown(f"**{key}**")
            for item in timescale_comparison[key]:
                st.markdown(f"_{item}_")

    st.info("""
    **Key Insight:** Cascade timescales vary dramatically by region. Wealthier regions with
    distributed, redundant infrastructure experience slower cascades but have greater recovery
    capacity. Poorer regions experience faster cascades and have minimal recovery capacity.
    This creates a cruel asymmetry: Most vulnerable regions cascade fastest and recover slowest.
    """)

    st.divider()

    # SECTION 2: Global System Interdependencies
    st.subheader("[GLOBAL] Global System Coupling & Interdependencies")

    st.markdown("""
    Critical systems are tightly coupled globally through:
    - **Energy dependency:** Electricity needed for water, food, communications
    - **Trade dependency:** Food/fertilizer concentrated in few regions; all regions depend on semiconductors from Taiwan
    - **Financial dependency:** Crop failures → commodity price spikes → economic cascades globally
    - **Climate dependency:** Monsoons, droughts, extreme weather trigger regional failures with global ripple effects
    """)

    st.subheader("[POINT] Example Cascade Paths")

    cascade_examples = [
        {
            'trigger': 'Taiwan semiconductor production stops',
            'cascade': 'Semiconductors → Renewable energy deployment halts → Grid modernization stops → Electrical vulnerability increases → Crisis risk peaks',
            'global': 'Every developed nation unable to upgrade infrastructure'
        },
        {
            'trigger': 'Mekong monsoon fails (Southeast Asia)',
            'cascade': 'Water → Crop failure → Food shortage → Price spike → Conflict → 60M+ displaced → Migration pressure',
            'global': 'Regional destabilization, refugee crisis in Europe/Middle East'
        },
        {
            'trigger': 'Russian fertilizer/wheat export blocked',
            'cascade': 'Fertilizer → Global crop yields decline → Food shortage → Price spike → Social unrest → Supply chains freeze',
            'global': 'Sub-Saharan Africa, South Asia most vulnerable; food security crisis'
        },
        {
            'trigger': 'North American grid collapse',
            'cascade': 'Grid → Water/fuel/food fail → Recovery infrastructure overwhelmed → Supply chains freeze → Food exports stop',
            'global': 'Global grain shortage (Canada wheat, US corn, fertilizer from potash production)'
        },
    ]

    for idx, example in enumerate(cascade_examples, 1):
        st.markdown(f"**{idx}. {example['trigger']}**")
        st.markdown(f"_Cascade:_ {example['cascade']}")
        st.markdown(f"_Global:_ {example['global']}")
        if idx < len(cascade_examples):
            st.divider()

    st.warning("""
    **Critical Finding:** No critical system fails in isolation. Energy, food, water, semiconductors,
    and financial systems are globally coupled. A failure in one region triggers cascades across all
    others through trade, energy, and financial interdependencies.
    """)

    st.divider()

    # SECTION 3: Asymmetric Timescales
    st.subheader("[TIME] The Asymmetry Problem: Destruction vs. Reconstruction")

    st.markdown("""
    The most dangerous insight: it takes 20 minutes to destroy what takes 18+ months to rebuild.
    This 500-1000x asymmetry means no amount of defensive hardening can match the speed gap.
    """)

    asym_data = {
        'Phase': ['Attack/Destruction', 'Detection & Response', 'Repair & Replacement', 'Full Recovery'],
        'Duration': ['20 minutes', '6-12 hours', '6-18 months', '2-5 years'],
        'What Happens': [
            '17 transformers disabled by 2 trained attackers',
            'Response teams mobilized; power not restored',
            'Replacement transformers sourced and installed',
            'Grid fully operational; society restored'
        ]
    }

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Phase**")
        for phase in asym_data['Phase']:
            st.markdown(f"_{phase}_")

    with col2:
        st.markdown("**Duration**")
        for duration in asym_data['Duration']:
            st.markdown(f"**{duration}**")

    with col3:
        st.markdown("**What's Happening**")
        for event in asym_data['What Happens']:
            st.markdown(event)

    # Asymmetry ratio visualization
    st.markdown("---")
    st.markdown("**Asymmetry Ratio: ~500–1000x**")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Destruction timeline:** 20 minutes")
        st.markdown("*Metcalf substation attack proved this operational capability*")

    with col2:
        st.markdown("**Reconstruction timeline:** 18+ months (at current capacity)")
        st.markdown("*Transformer lead times: 128 weeks; production cannot surge*")

    st.error("""
    **Implication:** Traditional thinking says "build redundancy, harden defenses."
    But this asymmetry means defensive hardening cannot scale fast enough to matter.
    Strategy must shift from defense to resilience.
    """)

# ============================================
# 3. THREAT LANDSCAPE
# ============================================
def section_threat_landscape():
    st.header("[TARGET] Geopolitical Threats to Global Critical Infrastructure")

    st.markdown("""
    Critical infrastructure globally is not just vulnerable to natural disasters or accidents.
    It is an active target for state and non-state actors with demonstrated capability, intent,
    and opportunity. Threats vary by region and by system, but all create cascade risk.
    """)

    # STATE ACTOR THREATS
    st.subheader("[GLOBAL] State Actor Threats by Region & Target System")

    threats = [
        {
            'country': '[CHINA] China',
            'targets': ['US electrical grid', 'Semiconductor supply chains', 'South Asian water systems', 'African infrastructure'],
            'capability': 'Software backdoors in transformers; supply chain manipulation; cyber reconnaissance',
            'intent': 'Reduce US technological advantage; secure resource access; undermine rival infrastructure',
            'threat_level': '[CRITICAL] CRITICAL'
        },
        {
            'country': '[RUSSIA] Russia',
            'targets': ['European electrical grid', 'European energy systems', 'Global grain/fertilizer systems', 'NATO infrastructure'],
            'capability': 'Demonstrated cyber attacks on electrical systems; energy weaponization; supply chain control',
            'intent': 'Destabilize Europe economically; secure energy leverage; disrupt supply chains',
            'threat_level': '[CRITICAL] CRITICAL'
        },
        {
            'country': '[IRAN] Iran',
            'targets': ['Middle East water systems', 'Regional electrical grids', 'Global energy markets', 'Regional rivals'],
            'capability': 'Water system sabotage; cyber operations; asymmetric tactics',
            'intent': 'Regional dominance; destabilization of rivals; resilience building',
            'threat_level': '[CRITICAL] CRITICAL'
        },
        {
            'country': '[NORTH_KOREA] North Korea',
            'targets': ['Financial systems', 'Critical infrastructure cyber access', 'Energy/food systems'],
            'capability': 'Sophisticated cyber operations; supply chain infiltration; asymmetric tactics',
            'intent': 'Sanctions evasion; economic disruption; regime survival',
            'threat_level': '[WARNING] SERIOUS'
        },
    ]

    for threat in threats:
        with st.container():
            col1, col2 = st.columns([1, 3])
            with col1:
                st.markdown(f"**{threat['country']}**")
                st.markdown(threat['threat_level'])
            with col2:
                st.markdown(f"**Targets:** {', '.join(threat['targets'])}")
                st.markdown(f"**Capability:** {threat['capability']}")
                st.markdown(f"**Intent:** {threat['intent']}")
            st.divider()

    # METCALF AS OPERATIONAL TEMPLATE
    st.subheader("[CONFLICT] Metcalf Attack: Operational Template for Extremists")

    st.markdown("""
    The 2013 Metcalf substation attack proved the concept. It has since become
    a model studied by extremist groups for years.
    """)

    metcalf_facts = {
        'Date': 'April 16, 2013',
        'Location': 'Metcalf Substation, San Jose, CA',
        'Attackers': '2 trained shooters',
        'Duration': '20 minutes',
        'Result': '17 transformers disabled; power lost to sections of Silicon Valley',
        'Training': 'Very carefully planned and precisely executed',
        'Knowledge': 'Attackers knew which cables to cut, which transformer parts to hit, exact police arrival time',
    }

    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("**Attack Specs**")
        for key in metcalf_facts.keys():
            st.markdown(f"_{key}_")

    with col2:
        st.markdown("**Details**")
        for value in metcalf_facts.values():
            st.markdown(f"**{value}**")

    st.warning("""
    **What This Proves:** The attack was not luck or improvisation.
    Attackers had detailed knowledge of:
    - Which infrastructure to target
    - Exact timing and sequence
    - When law enforcement would arrive

    This expertise is now widely available to extremist networks.
    """)

    # TIMELINE OF INCIDENTS
    st.subheader("[DATE] Timeline of Known Attacks & Threats")

    incidents = [
        {'date': 'April 16, 2013', 'incident': 'Metcalf substation attack — 17 transformers disabled', 'actor': 'Unknown (likely domestic extremists)', 'impact': 'Proof of concept'},
        {'date': 'December 3, 2022', 'incident': 'Moore County NC — transformers disabled; 45,000 lost power for up to 5 days', 'actor': 'Unknown extremists', 'impact': 'Pattern replication'},
        {'date': '2024', 'incident': 'Five white supremacist group members sentenced for plotting to destroy transformers', 'actor': 'Domestic extremists', 'impact': 'Intent confirmed'},
        {'date': 'August 2026', 'incident': 'Iran linked to water system sabotage', 'actor': 'State actor', 'impact': 'Active campaign'},
        {'date': 'August 2026', 'incident': 'China software backdoor discovered in U.S. transformer', 'actor': 'State actor', 'impact': 'Embedded threat'},
    ]

    for idx, incident in enumerate(incidents):
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            st.markdown(f"**{incident['date']}**")
        with col2:
            st.markdown(f"**{incident['incident']}**")
            st.caption(f"Actor: {incident['actor']}")
        with col3:
            st.markdown(f"_{incident['impact']}_")
        if idx < len(incidents) - 1:
            st.divider()

    # THREAT ASSESSMENT
    st.subheader("[ALERT] Risk Assessment")

    risk_factors = [
        ("Known operational capability", "Metcalf proved the attack is executable with 2 trained operatives"),
        ("Demonstrated intent", "Multiple extremist groups actively plotting; state actors conducting operations"),
        ("Opportunity increasing", "Extremist networks are studying Metcalf model; state actors investing in capabilities"),
        ("System vulnerability", "No comprehensive hardening standard; many substations still undefended"),
        ("Detection lag", "Attacks discovered after damage; no predictive detection system exists"),
        ("Acceleration trend", "From Metcalf (2013) → Moore County (2022) → extremist convictions (2024)")
    ]

    for factor, description in risk_factors:
        st.markdown(f"• **{factor}:** {description}")

    st.error("""
    **Conclusion:** The grid is not just technically vulnerable. It is an active target
    for sophisticated actors who have demonstrated capability and intent. The timeline
    shows escalating activity (state actors now openly conducting operations).
    Without major changes, expect more frequent attacks as capabilities proliferate.
    """)

# ============================================
# 4. SUPPLY CHAIN CONSTRAINTS
# ============================================
def section_supply_chain_constraints():
    st.header("[WORLD] Global Supply Chain Fragility — Critical Bottlenecks")

    st.markdown("""
    Global critical systems depend on concentrated supply chains that cannot surge production
    in response to crisis. Multiple systems face structural bottlenecks (not economic ones)
    that prevent rapid scaling.
    """)

    # SYSTEM 1: SEMICONDUCTORS
    st.subheader("[SYSTEM] Bottleneck 1: Semiconductor Production — Taiwan Concentration")

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""
        **The Problem:**
        - Taiwan produces 92% of advanced semiconductors globally
        - Semiconductors needed for: renewable energy, grid modernization, AI infrastructure, water treatment, food systems
        - Cannot substitute; no alternative production capacity
        - Taiwan politically unstable; military risk high

        **Implication:**
        - Geopolitical tension → semiconductor access interrupted → renewable deployment halts → infrastructure modernization stops
        - Every developed nation's energy transition depends on Taiwan's continued exports
        - War or political isolation = multi-year technology freeze globally

        **Current State:**
        - TSMC (Taiwan) dominates leading-edge chip production
        - No redundancy; South Korea (Samsung) is backup but also vulnerable
        - New fabs take 3-5 years to build
        """)

    with col2:
        st.markdown("**Status**")
        st.metric("Taiwan share", "92%")
        st.metric("Alternative supply", "Minimal")
        st.metric("Fab build time", "3-5 yrs")
        st.metric("Geopolitical risk", "HIGH")

    st.warning("**Constraint type:** Geopolitical + Manufacturing")

    st.divider()

    # SYSTEM 2: FERTILIZER
    st.subheader("[AGRICULTURE] Bottleneck 2: Fertilizer Production — Energy & Geography Dependent")

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""
        **The Problem:**
        - Nitrogen fertilizer production requires cheap natural gas (energy-intensive)
        - Russia + Belarus produce 30%+ of global potash (K fertilizer)
        - Global grain system depends on this fertilizer supply
        - Production cannot surge; it's energy-limited, not capital-limited

        **Implication:**
        - Energy price spike → fertilizer price spike → grain yield decline → food shortage
        - Geopolitical sanctions (Russia) → fertilizer supply cut → global food crisis
        - Sub-Saharan Africa and South Asia most vulnerable (lowest stored reserves)

        **Current State:**
        - Fertilizer prices already volatile post-Ukraine war
        - Global grain stocks at 2-month coverage (historically 3+ months)
        - Production capacity fixed by available cheap energy
        """)

    with col2:
        st.markdown("**Status**")
        st.metric("Russia share", "30%+")
        st.metric("Global reserves", "2 months")
        st.metric("Price volatility", "HIGH")
        st.metric("Surge capacity", "Limited")

    st.warning("**Constraint type:** Energy + Geopolitics")

    st.divider()

    # SYSTEM 3: RARE EARTHS
    st.subheader("[CRITICAL] Bottleneck 3: Rare Earth Elements — China Dominance")

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""
        **The Problem:**
        - China produces 75%+ of refined rare earth elements globally
        - Rare earths needed for: wind turbines, electric vehicles, renewable systems, military equipment
        - Cannot substitute; mining is easy but refining is specialized
        - China has strategic reserves and export controls

        **Implication:**
        - Geopolitical tension → export restriction → renewable deployment halts → energy transition stops
        - U.S./Europe cannot quickly build refining capacity (years-long process)
        - Climate solution (renewables) depends on China's good will

        **Current State:**
        - China controls 75%+ of refining globally
        - New refining capacity takes 2-3 years
        - Export controls already used as geopolitical tool
        """)

    with col2:
        st.markdown("**Status**")
        st.metric("China share", "75%+")
        st.metric("Alternative refining", "Minimal")
        st.metric("Refinery build time", "2-3 yrs")
        st.metric("Political risk", "HIGH")

    st.warning("**Constraint type:** Geopolitics + Specialized Manufacturing")

    st.divider()

    # SYNTHESIS
    st.subheader("[WORLD] Structural Supply Chain Fragility")

    st.markdown("""
    **Pattern:** Critical systems all depend on geographically concentrated, politically vulnerable supply chains
    that cannot surge production in response to crisis.
    """)

    bottleneck_matrix = {
        'System': ['Semiconductors', 'Fertilizer', 'Rare Earths', 'Electrical Transformers'],
        'Concentration': ['Taiwan 92%', 'Russia 30%+ (potash)', 'China 75% (refining)', '1 U.S. GOES mill'],
        'Political Risk': ['High (China)', 'High (Russia)', 'High (China)', 'Moderate'],
        'Surge Capacity': ['3-5 yrs', 'Energy-limited', '2-3 yrs', '1.2x maximum'],
        'Global Impact': ['Tech freeze', 'Food crisis', 'Energy transition halts', 'Grid blackout'],
    }

    col1, col2, col3, col4, col5 = st.columns(5)
    cols = [col1, col2, col3, col4, col5]

    for idx, key in enumerate(bottleneck_matrix.keys()):
        with cols[idx]:
            st.markdown(f"**{key}**")
            for item in bottleneck_matrix[key]:
                st.markdown(f"_{item}_")

    st.error("""
    **Conclusion:** These bottlenecks are STRUCTURAL. They cannot be solved by:
    - Capital investment (facilities take years to build; mining/refining are specialized)
    - Policy mandates (concentration is geographic/geopolitical, not regulatory)
    - International cooperation (conflicting interests, political risk high)

    Any crisis that disrupts these supply chains cascades globally with no quick recovery pathway.
    """)

# ============================================
# 5. SOLUTIONS & TECHNOLOGY HORIZON
# ============================================
def section_solutions_horizon():
    st.header("[PREDICTION] Technology Deployment & Regional Variance")

    st.markdown("""
    Promising solutions exist, but deployment timelines vary dramatically by region and technology type.
    Developed economies deploying faster, but most vulnerable regions (Sub-Saharan Africa, South Asia)
    lag years behind. This creates new asymmetries: Rich regions solve their problems; poor regions don't.
    """)

    st.subheader("[TIME] The Timing Problem — Solution vs. Crisis")

    st.markdown("""
    **Crisis Timeline:** Hours to days (geopolitical shocks, cyber attacks, natural disasters)
    **Technology Timeline:** 5-10+ years to global deployment at crisis-solving scale

    This creates a cruel asymmetry: Solutions exist, but arrive too late. And they arrive
    unevenly: developed economies deploy first and fastest; vulnerable regions get nothing.
    """)

    st.divider()

    # SOLUTIONS BY REGION
    st.subheader("[WORLD] Technology Deployment by Region (2026-2034)")

    region_solutions = {
        'North America': {
            'battery': 'Deployment underway; doubling 2025-27',
            'renewable': 'Wind/solar fast deployment; 2027 ~30% capacity',
            'sst': '2034+ deployment starting',
            'water': 'Desalination tech available; capital-constrained',
            'overall': '[CAUTION] Moderate—capital available but supply chain delays'
        },
        'Europe': {
            'battery': 'Fast deployment; doubling 2025-27',
            'renewable': 'Aggressive targets; 2027 ~40% capacity',
            'sst': '2032+ deployment (earlier than US)',
            'water': 'Already investing; tech solutions available',
            'overall': '[GOOD] Good—policy coordination, capital available'
        },
        'Asia-Pacific': {
            'battery': 'China leading; variable others (2028+)',
            'renewable': 'China fast (40%+), India moderate, others slow',
            'sst': '2035+ (China may lead)',
            'water': 'Monsoon-dependent; tech lag; minimal deployment',
            'overall': '[CAUTION] Mixed—China advances, others lag'
        },
        'Sub-Saharan Africa': {
            'battery': 'Minimal deployment; 2035+ likely',
            'renewable': 'Solar potential high; capital gap severe',
            'sst': '2040+ or never (import-dependent)',
            'water': 'Desalination unaffordable; groundwater depleting',
            'overall': '[CRITICAL] Poor—capital gap, tech lag, climate stress'
        }
    }

    for region, solutions in region_solutions.items():
        with st.container():
            st.markdown(f"**{region}** — {solutions['overall']}")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.caption("**Battery Storage**")
                st.markdown(solutions['battery'])
            with col2:
                st.caption("**Renewable Deployment**")
                st.markdown(solutions['renewable'])
            with col3:
                st.caption("**SST Timeline**")
                st.markdown(solutions['sst'])
            with col4:
                st.caption("**Water Solutions**")
                st.markdown(solutions['water'])
            st.divider()

    st.divider()

    # SYNTHESIS: TECHNOLOGY VS CRISIS TIMELINE
    st.subheader("[UP] Technology Availability vs. Crisis Acceleration")

    timeline_viz = {
        'Year': ['2026', '2027', '2028', '2029', '2030', '2031', '2032', '2033', '2034+'],
        'Crisis Risk Level': ['High', 'High', 'High', 'Very High', 'Critical', 'Critical', 'Critical', 'Critical', 'Critical'],
        'SST Readiness': ['Lab', 'Lab', 'Lab', 'Lab', 'Early Commercial', 'Early Commercial', 'Scaling', 'Scaling', 'Ready'],
        'Battery Doubling': ['Ongoing', 'Peak', 'Post-Peak', 'Mature', 'Mature', 'Mature', 'Mature', 'Mature', 'Mature'],
    }

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("**Year**")
        for year in timeline_viz['Year']:
            st.markdown(f"_{year}_")

    with col2:
        st.markdown("**Crisis Risk**")
        for risk in timeline_viz['Crisis Risk Level']:
            if 'Critical' in risk:
                st.markdown(f"[CRITICAL] **{risk}**")
            elif 'Very High' in risk:
                st.markdown(f"[WARNING] **{risk}**")
            else:
                st.markdown(f"[CAUTION] **{risk}**")

    with col3:
        st.markdown("**SST Readiness**")
        for status in timeline_viz['SST Readiness']:
            st.markdown(status)

    with col4:
        st.markdown("**Battery Status**")
        for status in timeline_viz['Battery Doubling']:
            st.markdown(status)

    st.error("""
    **The Bifurcation:** Crisis risk peaks (2026-2034+) while solutions become available
    (2034+). There is a 5-8 year window where crisis is most likely but solutions are not
    yet deployed at scale.

    **What This Means:** We have solutions coming, but we need them NOW. The intervention
    window for the next ~5-8 years relies on hardening, resilience, and institutional
    capacity—not technological solutions.
    """)

# ============================================
# 6. STRATEGIC BLIND SPOTS
# ============================================
def section_strategic_blind_spots():
    st.header("[DETECTIVE] Global Measurement Blindness & Systemic Unknowns")

    st.markdown("""
    No region has comprehensive visibility into its own critical infrastructure status or
    its vulnerabilities. And the regions with the lowest visibility (Sub-Saharan Africa, South Asia)
    are the most vulnerable to cascade failure. This creates strategic vulnerability at global scale.
    """)

    st.subheader("[CHART] What We Cannot See Globally")

    unknowns = [
        {
            'category': 'Transformer Inventory & Condition',
            'blind_spot': 'No comprehensive inventory of transformer age/condition across 55,000+ substations',
            'implication': 'Do not know which units are close to failure; cannot predict next failure'
        },
        {
            'category': 'Critical Node Mapping',
            'blind_spot': 'FERC identified "top 10" critical substations but did not publish the list',
            'implication': 'Adversaries must map vulnerabilities; we have classified the critical nodes'
        },
        {
            'category': 'Interdependency Mapping',
            'blind_spot': 'No unified model of cascade pathways across water/fuel/food/communications systems',
            'implication': 'Cannot predict how failures will propagate; modeling uncertainty is severe'
        },
        {
            'category': 'Adversary Capabilities',
            'blind_spot': 'Vulnerabilities discovered by attacks (Metcalf 2013, Moore County 2022), not proactive assessment',
            'implication': 'Attackers find vulnerabilities faster than we can harden them'
        },
        {
            'category': 'Security Status of Substations',
            'blind_spot': '55,000 substations with uneven physical security; no unified assessment',
            'implication': 'DHS explicit: "You can\'t protect everything"'
        },
    ]

    for unknown in unknowns:
        with st.container():
            st.markdown(f"**{unknown['category']}**")
            st.markdown(f"_Blind Spot:_ {unknown['blind_spot']}")
            st.caption(f"[POINT] {unknown['implication']}")
            st.divider()

    st.warning("""
    **Why This Matters:**

    Strategic uncertainty creates strategic vulnerability. The more we don't know about
    our own system, the more vulnerable it is to those who are actively mapping it.

    Adversaries have incentive and time to find weaknesses. We have neither—and we are
    flying blind about what they have already found.
    """)

    st.subheader("[REFRESH] The Asymmetry of Information")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**What We Know**")
        st.markdown("""
        • General grid architecture
        • Some failure modes (learned from past attacks)
        • Transformer age distribution (approximate)
        • Policy responses (documented)
        """)

    with col2:
        st.markdown("**What Adversaries Know**")
        st.markdown("""
        • Specific vulnerable nodes (from reconnaissance)
        • Optimal attack sequences (from Metcalf analysis)
        • Guard schedules and response times (surveillance)
        • Critical infrastructure dependencies (study)
        """)

    st.error("""
    **The problem isn't that we have blind spots. The problem is that our blind spots
    are being systematically mapped by actors with both incentive and time.**
    """)

# ============================================
# 7. GLOBAL INFRASTRUCTURE WATCH
# ============================================
def section_global_infrastructure_watch():
    st.header("[BROADCAST] Global Critical Infrastructure Watch")

    st.markdown("""
    Real-time monitoring of critical infrastructure developments globally with cascade implications.
    This page tracks ongoing developments in electrical grids, water systems, food systems, semiconductors,
    and critical materials that affect cascade risk.
    """)

    st.subheader("[CRITICAL] Electrical Grid Status by Region")

    grid_status = {
        'Region': ['North America', 'Europe', 'Asia-Pacific', 'Sub-Saharan Africa'],
        'Grid Age': ['38-40 years (aging)', 'Post-war infrastructure', 'Mixed (new-old)', 'Limited/fragmented'],
        'Transformer Capacity': ['120-week lead times', '100-week lead times', '150+ week lead times', 'Chronic shortage'],
        'Recent Incidents': ['Moore County 2022', 'Occasional attacks', 'Natural disasters', 'Infrastructure failure'],
        'Threat Level': ['[WARNING] High', '[WARNING] High', '[CRITICAL] Critical', '[CRITICAL] Critical'],
    }

    for i, region in enumerate(grid_status['Region']):
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.markdown(f"**{region}**")
        with col2:
            st.markdown(grid_status['Grid Age'][i])
        with col3:
            st.markdown(grid_status['Transformer Capacity'][i])
        with col4:
            st.markdown(grid_status['Recent Incidents'][i])
        with col5:
            st.markdown(grid_status['Threat Level'][i])
        st.divider()

    st.subheader("[WATER] Water System Status by Region")

    water_status = {
        'Region': ['North America', 'Europe', 'South Asia', 'Sub-Saharan Africa'],
        'Status': ['Colorado River critically low; Great Lakes stable', 'Abundant but aging infrastructure', 'Monsoon-dependent; aquifer depletion', 'Severe drought (Lake Chad, etc.)'],
        'Vulnerability': ['[CAUTION] High drought risk', '[GOOD] Moderate (reserves available)', '[CRITICAL] Very high (60M+ at risk)', '[CRITICAL] Critical (humanitarian)'],
        'Trend': ['Worsening', 'Stable', 'Degrading', 'Degrading fast'],
    }

    for i, region in enumerate(water_status['Region']):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"**{region}**")
        with col2:
            st.markdown(water_status['Status'][i])
        with col3:
            st.markdown(water_status['Vulnerability'][i])
        with col4:
            st.markdown(f"_{water_status['Trend'][i]}_")
        st.divider()

    st.subheader("[AGRICULTURE] Food & Agriculture System Status")

    st.markdown("""
    **Global Grain Stocks:** 2 months coverage (historically 3+ months)
    **Fertilizer Prices:** Volatile (Ukraine, Russia sanctions)
    **Regional Vulnerabilities:**
    - Sub-Saharan Africa: Dependent on grain imports; low storage capacity
    - South Asia: Monsoon-dependent; India rice export restrictions tightening
    - North America: Export surplus but supply chain concentrated
    """)

    st.divider()

    st.subheader("[SYSTEM] Semiconductor & Critical Materials Status")

    st.markdown("""
    **Semiconductors:** Taiwan production 92%; geopolitical risk HIGH
    - SST (Solid-State Transformers) still in prototype; deployment 2034+
    - AI chip demand surging; capacity stressed

    **Rare Earths:** China 75% refining; export controls tightening
    - Renewable energy deployment constrained by rare earth availability
    - New refining capacity takes 2-3 years; none under construction

    **Fertilizer:** Russia/Belarus 30%+ potash; energy-dependent nitrogen
    - Supply chain vulnerability high; price spikes cascade to food systems
    """)

    st.divider()

    st.subheader("[ALERT] Escalation Indicators (Watching These Metrics)")

    st.markdown("""
    **Electrical Grid Metrics:**
    - Transformer lead times (baseline: 128 weeks; critical: 150+ weeks)
    - Attack frequency (baseline: 1-2/year; concerning: 3+/year)
    - Grid utilization rates (baseline: 70-80%; concerning: 85%+)

    **Water System Metrics:**
    - Lake Powell/Mead levels (baseline: 35% capacity; critical: <20%)
    - Monsoon rainfall variance (baseline: ±10%; concerning: ±20%+)
    - Groundwater depletion rates (baseline: historical; concerning: accelerating)

    **Food System Metrics:**
    - Global grain reserves (baseline: 3+ months; critical: <2 months)
    - Fertilizer prices (baseline: $50-60/ton; concerning: $100+/ton)
    - Regional import dependencies (tracking: Sub-Saharan Africa grain imports increasing)

    **Supply Chain Metrics:**
    - Taiwan fab utilization (baseline: 80-90%; concerning: 95%+)
    - Semiconductor lead times (baseline: 12 weeks; concerning: 26+ weeks)
    - Rare earth refining bottlenecks (baseline: current; concerning: new restrictions)
    """)

# ============================================
# CONTINUE: RESEARCH FINDINGS DETAILS
# ============================================

    mechanisms = list(set([f['mechanism'] for f in project_findings])) if project_findings else []
    mechanisms.sort()

    selected_mechanism = st.selectbox(
        "Filter by Mechanism",
        ["All Mechanisms"] + mechanisms,
        index=0
    )

    if selected_mechanism == "All Mechanisms":
        findings = project_findings
    else:
        findings = [f for f in project_findings if f['mechanism'] == selected_mechanism]

    if findings:
        # Group findings by confidence level for better visualization
        critical_conf = [f for f in findings if f['confidence_level'] >= 0.85]
        high_conf = [f for f in findings if 0.75 <= f['confidence_level'] < 0.85]
        moderate_conf = [f for f in findings if f['confidence_level'] < 0.75]

        # Display critical confidence findings
        if critical_conf:
            st.subheader("[GOOD] High Confidence (≥85%)")
            for finding in critical_conf:
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**{finding['mechanism']}**")
                        st.write(finding['finding_text'])
                    with col2:
                        st.metric("Confidence", f"{finding['confidence_level']:.0%}")
                    if finding['supporting_evidence']:
                        st.caption(f"[POINT] Evidence: {finding['supporting_evidence']}")
                    st.divider()

        # Display high confidence findings
        if high_conf:
            with st.expander(f"[CAUTION] Moderate-High Confidence (75-85%)", expanded=False):
                for finding in high_conf:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**{finding['mechanism']}**")
                        st.write(finding['finding_text'])
                    with col2:
                        st.metric("Confidence", f"{finding['confidence_level']:.0%}")
                    if finding['supporting_evidence']:
                        st.caption(f"[POINT] Evidence: {finding['supporting_evidence']}")
                    st.divider()

        # Display moderate confidence findings
        if moderate_conf:
            with st.expander(f"[INFO] Emerging Findings (<75%)", expanded=False):
                for finding in moderate_conf:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**{finding['mechanism']}**")
                        st.write(finding['finding_text'])
                    with col2:
                        st.metric("Confidence", f"{finding['confidence_level']:.0%}")
                    if finding['supporting_evidence']:
                        st.caption(f"[POINT] Evidence: {finding['supporting_evidence']}")
                    st.divider()
    else:
        st.info("No findings available for selected mechanism.")

    st.markdown("---")

    # Confidence distribution chart
    st.subheader("[UP] Confidence Distribution")

    if findings:
        confidence_data = {
            'Critical (≥85%)': len(critical_conf),
            'High (75-85%)': len(high_conf),
            'Emerging (<75%)': len(moderate_conf)
        }

        fig_dist = go.Figure(data=[
            go.Pie(
                labels=list(confidence_data.keys()),
                values=list(confidence_data.values()),
                marker=dict(colors=['#87d03b', '#fab219', '#ec835a']),
                textinfo='label+value',
                hovertemplate='<b>%{label}</b><br>Count: %{value}<extra></extra>'
            )
        ])

        fig_dist.update_layout(
            height=400,
            font=dict(size=12)
        )

        st.plotly_chart(fig_dist)

        # Timeline of discoveries
        st.subheader("[DATE] Findings Timeline")

        findings_sorted = sorted(findings, key=lambda x: x['date_discovered'])
        timeline_df = pd.DataFrame({
            'Date': [f['date_discovered'] for f in findings_sorted],
            'Mechanism': [f['mechanism'] for f in findings_sorted],
            'Confidence': [f['confidence_level'] for f in findings_sorted],
            'Finding': [f['finding_text'][:60] + '...' for f in findings_sorted]
        })

        # Create mechanism-to-symbol mapping for secondary encoding
        unique_mechanisms = timeline_df['Mechanism'].unique()
        marker_symbols = ['circle', 'diamond', 'square', 'cross', 'x', 'triangle-up', 'triangle-down', 'star']
        mech_symbol_map = {mech: marker_symbols[i % len(marker_symbols)] for i, mech in enumerate(unique_mechanisms)}
        timeline_df['symbol'] = timeline_df['Mechanism'].map(mech_symbol_map)

        fig_timeline = px.scatter(
            timeline_df,
            x='Date',
            y='Confidence',
            color='Mechanism',
            symbol='Mechanism',
            size=[4]*len(timeline_df),
            hover_data=['Finding'],
            title='Research Findings Discovery Timeline (Color + Shape identify mechanism)',
            height=400
        )

        fig_timeline.update_layout(
            hovermode='closest',
            font=dict(size=11),
            yaxis=dict(tickformat='.0%'),
            legend=dict(yanchor='top', y=0.99, xanchor='right', x=0.99)
        )

        st.plotly_chart(fig_timeline)

# ============================================
# 8. POLICY GAP ANALYSIS
# ============================================
def section_policy_gap_analysis():
    st.header("[CHART] Gap Analysis: Response vs. Crisis Reality")

    st.markdown("""
    **Core Problem:** Current policy responses are structurally insufficient to address cascade risks.
    The gap between response timescales and crisis timescales is unbridgeable by current mechanisms.
    """)

    st.subheader("[SHIELD] Policy Responses Attempted")

    responses = [
        {
            'policy': 'Defense Production Act (2022, 2026)',
            'action': 'Invoked twice to accelerate transformer production',
            'outcome': 'Minimal effect on lead times',
            'timeline_impact': '128 weeks → 120 weeks (8-week reduction only)',
            'assessment': '[CRITICAL] Ineffective'
        },
        {
            'policy': 'Tax Credits (Inflation Reduction Act)',
            'action': 'Encouraged factory expansion (Siemens, ABB)',
            'outcome': 'Factories planned but still 3-5 years to build',
            'timeline_impact': 'New capacity available 2028-2030',
            'assessment': '[CAUTION] Too late'
        },
        {
            'policy': 'Voluntary Equipment-Sharing Program',
            'action': 'Utilities encouraged to share spare transformers',
            'outcome': 'Useless (each transformer is unique/bespoke)',
            'timeline_impact': 'Zero impact',
            'assessment': '[CRITICAL] Irrelevant'
        },
        {
            'policy': 'GridEx War Games',
            'action': 'Simulation-based preparedness exercises',
            'outcome': 'Optional participation; no binding outcomes',
            'timeline_impact': 'No operational readiness improvement',
            'assessment': '[CRITICAL] Voluntary/toothless'
        }
    ]

    for i, response in enumerate(responses):
        col1, col2, col3, col4, col5 = st.columns([1.5, 1.5, 1.5, 1.5, 1])
        with col1:
            st.markdown(f"**{response['policy']}**")
        with col2:
            st.markdown(response['action'])
        with col3:
            st.markdown(response['outcome'])
        with col4:
            st.markdown(response['timeline_impact'])
        with col5:
            st.markdown(response['assessment'])
        st.divider()

    st.subheader("[FAILED] Why These Responses Are Insufficient")

    reasons = [
        {
            'reason': 'Timescale Mismatch',
            'description': 'Crisis unfolds in hours-days; policy responses take years',
            'example': 'Blackout cascade: 0-20 min (attack) → 72 hours (system collapse). DPA action: months to implement.',
            'constraint': 'STRUCTURAL'
        },
        {
            'reason': 'Structural Constraints Ignored',
            'description': 'Policy targets economics; problem is technical (handcraft, single-point failures)',
            'example': 'Transformer production: 11,000+ unique designs. Cannot standardize or surge. Cannot substitute GOES steel.',
            'constraint': 'STRUCTURAL'
        },
        {
            'reason': 'Capital Inadequacy',
            'description': 'Recovery cost ($2.5B+ for 180-unit cascade) exceeds disaster response budgets',
            'example': 'FEMA emergency response budget: ~$1B/year. Cascade recovery: $2.5B+ minimum, plus humanitarian response.',
            'constraint': 'FINANCIAL'
        },
        {
            'reason': 'Coordination Mechanisms Don\'t Exist',
            'description': 'No international framework for cross-border coordination',
            'example': 'Grain shortage cascades globally; no treaty mechanism for synchronized supply management.',
            'constraint': 'INSTITUTIONAL'
        }
    ]

    for reason in reasons:
        st.markdown(f"""
        **{reason['reason']}** [{reason['constraint']}]
        - {reason['description']}
        - *Example:* {reason['example']}
        """)
        st.divider()

    st.subheader("[TIME] Timescale Comparison")

    st.markdown("""
    | Event | Timeline | Policy Response Possible? |
    |-------|----------|---------------------------|
    | **Attack on substations** | 0-20 minutes | [FAILED] No (already happened) |
    | **Water treatment failure** | 6-12 hours | [FAILED] No (happens during DPA review) |
    | **Fuel delivery collapses** | 24-48 hours | [FAILED] No (hospitals still online but vulnerable) |
    | **Food distribution fails** | 3-7 days | [WARNING] Emergency orders only (insufficient scale) |
    | **Supply chains freeze** | 1-4 weeks | [WARNING] International coordination impossible |
    | **Transformer replacement** | 12-18+ months | [YES] Only after crisis + recovery window |
    """)

    st.subheader("[ALERT] The Real Constraint: Adaptation Speed")

    st.markdown("""
    **Institutional learning lag:** Each major event teaches us something, but adversaries learn faster.
    - Metcalf attack (2013): Demonstrated vulnerability
    - Moore County attack (2022): Pattern replication proven
    - 2024 extremist convictions: Expertise now public
    - 2026: State actors targeting grid

    **The asymmetry:** We improve defenses after attacks. Adversaries study successful attacks faster than we can harden.

    **Conclusion:** Current response mechanisms assume slow-moving crises (gradual climate change, demographic shifts).
    They cannot address fast-moving cascade failures where window to act is measured in hours.
    """)

# ============================================
# 9. BIFURCATION POINT DIAGRAM
# ============================================
def section_bifurcation_point():
    st.header("[SHUFFLE] Bifurcation Point: Two Diverging System Paths")

    st.markdown("""
    **Strategic Context:** Global critical infrastructure systems are approaching a bifurcation point—
    a threshold where small perturbations trigger divergence into dramatically different futures.

    One path leads to managed degradation; the other to systemic collapse with no recovery pathway.
    """)

    st.subheader("[POINT] Evidence for Bifurcation")

    st.markdown("""
    **Threshold 1: Transformer Age Distribution (75% past service life)**
    - Distribution is not uniform; concentrated failure risk exists at 55,000+ substations
    - FERC analysis: 9 strategically targeted substations could black out entire U.S.
    - This is a discrete threshold, not gradual failure

    **Threshold 2: Supply Chain Saturation (Taiwan 92% semiconductor production)**
    - No redundancy; no alternative suppliers; no surge capacity beyond ~1.2x
    - Geopolitical tension → supply interruption → renewable deployment halts globally
    - This is not a dial; it's a switch

    **Threshold 3: Global Grain Reserves (2-month coverage vs historical 3+ months)**
    - System operates at edge of buffer capacity
    - Single regional crop failure (monsoon, drought) triggers global shortage
    - This system has lost slack; no room for error
    """)

    st.subheader("[TARGET] The Bifurcation Scenario")

    # Create a visual representation of the two paths
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Path A: Managed Degradation (Intervention Successful)")
        st.markdown("""
        **Starting condition:** Current state + protective hardening

        **Trigger threshold:** Limited disturbance (regional outage, localized shortage)

        **Cascade behavior:** Partial failures isolated by:
        - Distributed backup systems
        - Strategic reserves
        - International cooperation

        **Timeline:**
        - Years 1-3: System under stress but functional
        - Years 3-10: Continued decline in performance
        - Outcome: Functioning but constrained system

        **Requirements:**
        - [YES] Proactive hardening 2026-2028
        - [YES] Surge investment in alternatives (renewables, battery, SST)
        - [YES] International coordination mechanisms
        - [YES] Fair distribution of recovery capacity
        """)

    with col2:
        st.markdown("### Path B: Cascading Collapse (Intervention Fails)")
        st.markdown("""
        **Starting condition:** Current state + no additional hardening

        **Trigger threshold:** Multiple simultaneous disturbances (grid attack + monsoon + cyberattack)

        **Cascade behavior:** Runaway feedback:
        - Grid collapse → water/fuel/food fail → emergency response collapses
        - Supply chains freeze → manufacturing stops → recovery capacity disappears
        - Coordination failure → every region for itself → humanitarian crisis

        **Timeline:**
        - Minutes-hours: Cascading blackout
        - Hours-days: Food/water/fuel systems fail
        - Days-weeks: Social breakdown
        - Weeks-months: Supply chains globally frozen
        - Outcome: No recovery pathway; system stuck offline

        **Why recovery fails:**
        - [FAILED] Transformer replacement requires power (can't manufacture offline)
        - [FAILED] No supply chains = no parts = no restart
        - [FAILED] Capital reserves exhausted on emergency response
        - [FAILED] Interstate/international coordination impossible
        """)

    st.divider()

    st.subheader("[WARNING] Key Insight: This Is a Bifurcation, Not Gradual Decline")

    st.markdown("""
    **Why it's not just "more of the same":**

    Bifurcation points have three critical properties:

    1. **Threshold Behavior** — Small changes up to the threshold produce proportional effects.
    Beyond the threshold, tiny changes produce catastrophic divergence.

    2. **Non-Reversibility** — Once the threshold is crossed and cascade begins,
    reverting the trigger does NOT return the system to the original state.

    3. **Stability Loss** — The original "steady state" becomes unstable.
    The system cannot rest there even if we try to hold it.

    **In our system:**
    - Threshold: 9 substations attacked or simultaneous regional outages
    - Trigger: Exists now (expertise demonstrated at Metcalf 2013, Moore County 2022)
    - Probability: Increasing yearly with state actor interest + extremist knowledge

    **The closing window:**
    - Pre-bifurcation (now-2027): Hardening can push threshold higher
    - Bifurcation zone (2027-2030): Threshold becoming unreachable; divergence begins
    - Post-bifurcation (2030+): System locked into path; recovery impossible
    """)

    st.subheader("[UP] System State Over Time")

    # Simplified timeline visualization
    timeline_data = {
        'Year': [2026, 2027, 2028, 2029, 2030],
        'Intervention Successful': [100, 95, 85, 75, 60],  # Managed decline
        'No Intervention': [100, 98, 90, 60, 10]  # Cascading collapse
    }

    df_timeline = pd.DataFrame(timeline_data)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_timeline['Year'],
        y=df_timeline['Intervention Successful'],
        mode='lines+markers',
        name='Path A: Intervention Successful',
        line=dict(color='#3987e5', width=3),
        marker=dict(size=10)
    ))
    fig.add_trace(go.Scatter(
        x=df_timeline['Year'],
        y=df_timeline['No Intervention'],
        mode='lines+markers',
        name='Path B: No Intervention (Collapse)',
        line=dict(color='#d73838', width=3, dash='dash'),
        marker=dict(size=10)
    ))

    fig.update_layout(
        title='System Robustness Trajectories: Bifurcation Point Divergence',
        xaxis_title='Year',
        yaxis_title='System Robustness (%)',
        hovermode='x unified',
        template='plotly_dark',
        height=500,
        showlegend=True
    )
    fig.update_xaxes(gridcolor='#333333')
    fig.update_yaxes(gridcolor='#333333')

    st.plotly_chart(fig, width='stretch')

    st.subheader("[TARGET] Decision Point: Now")

    st.markdown("""
    **The intervention window is 2-4 years.**

    After 2027-2028, trajectory becomes increasingly locked:
    - Hardening installed systems help (push out cascade threshold)
    - Solutions technology coming online (SST 2034+, battery doubled 2027)
    - But global capacity for recovery continues to decline

    **If intervention succeeds:**
    - Managed decline: Functional system with performance constraints
    - Regional variation: Developed economies handle better; vulnerable regions need sustained aid
    - Recovery timescale: Years-decades, not impossible

    **If intervention fails:**
    - Cascade collapse: System offline, no recovery pathway
    - Global humanitarian crisis: Billions of people without water/food/power
    - Recovery timescale: Decades-centuries (if possible at all)

    **This is not prediction; it is architecture.** The system was designed without slack.
    The bifurcation exists in the mathematics of the problem, not the uncertainty of the future.
    """)

# ============================================
# ROUTINE EXECUTION HELPERS
# ============================================

def execute_routine(script_name, routine_name):
    """Execute a routine script and display output"""
    try:
        script_path = os.path.join(os.getcwd(), script_name)

        if not os.path.exists(script_path):
            st.error(f"Script not found: {script_path}")
            return

        st.info(f"Executing {routine_name}...")

        result = subprocess.run(
            ["python", script_path],
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode == 0:
            st.success(f"[OK] {routine_name} completed successfully")
            with st.expander("Show execution output"):
                st.code(result.stdout, language="text")
        else:
            st.error(f"[WARNING] {routine_name} completed with errors")
            with st.expander("Show error output"):
                st.code(result.stderr, language="text")

    except subprocess.TimeoutExpired:
        st.error(f"[TIME] {routine_name} timed out (exceeded 120 seconds)")
    except Exception as e:
        st.error(f"Error executing {routine_name}: {str(e)}")

def section_routines():
    """Automated routines and scanning tasks that run in the background"""
    st.header("[AI] Automated Routines")
    st.markdown("Background tasks and automation workflows designed by you, running continuously")

    st.subheader("Active Routines")

    # Routine 0: Hourly News Headline Scan (first in sequence)
    st.write("### [NEWS] Routine 0: Hourly News Headline Scan")
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.write("**Early Warning Monitoring**")
    with col2:
        st.write("Hourly")
    with col3:
        st.write(":24 past each hour")

    st.markdown("""
    **Data Source:** Multi-source news headline aggregation aligned with PROJECT GOALS (infrastructure, geopolitical, supply chain)

    **What It Does:**
    - Scans news headlines for events relevant to project goals
    - Monitors geopolitical events (sanctions, conflicts, trade restrictions)
    - Detects supply chain incidents (logistics delays, manufacturing disruptions)
    - Maps incidents to cascade nodes based on goal alignment
    - Adds early warning signals to research findings
    - Uses goal-driven analysis: all headlines scored against current project goals

    **Cascade Value:** Provides near-real-time detection of infrastructure failures with goal-aligned signal extraction. Single infrastructure incident cascades across dependent systems within hours. Hourly execution ensures rapid response to emerging events.

    **Status:** [OK] Active (Cloud-Based)
    - Script: `import_daily_news_headlines.py`
    - Trigger ID: `trig_01HmVDUDEhoHKiTXuRFc2tT7`
    - Scheduler: Cloud-based scheduled trigger (Streamlit Cloud infrastructure)
    - Frequency: Every hour at :24 minutes past (UTC)
    - No credentials needed (public news sources)
    """)

    col1, col2, col3 = st.columns([3, 1, 1])
    with col2:
        if st.button("[PLAY] Run Now", key="run_routine_0"):
            execute_routine("import_daily_news_headlines.py", "Daily News Headline Scan")
    with col3:
        st.write("")

    st.divider()

    # Routine 1: Hourly Gmail Message Analysis
    st.write("### [EMAIL] Routine 1: Hourly Gmail Message Analysis")
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.write("**Analyze All Emails**")
    with col2:
        st.write("Hourly")
    with col3:
        st.write(":48 past each hour")

    st.markdown("""
    **Data Source:** All Gmail folders (PRIMARY, UPDATES, custom labels, etc.) - any email with content relevant to PROJECT GOALS

    **What It Does:**
    - Connects to Gmail via IMAP (credentials stored locally in config.ini)
    - Scans ALL Gmail folders (PRIMARY, UPDATES, custom labels, etc.)
    - Tracks which messages have been analyzed by Message-ID to prevent duplicates
    - Extracts cascade-relevant signals from email content using goal-driven analysis
    - Scores email content against current project goals
    - Maps signals to cascade nodes based on goal alignment
    - Adds Research Findings with source attribution (sender, folder, subject)

    **Cascade Value:** Analyzes comprehensive email research from any source (Substack, work emails, newsletters, etc.), extracting goal-aligned insights without manual work. Hourly execution captures email-based signals rapidly. Tracks analyzed messages by native Message-ID to prevent reprocessing.

    **Status:** [OK] Active (Cloud-Based)
    - Script: `import_substack_imap.py` (refactored for all Gmail, goal-driven analysis)
    - Trigger ID: `trig_01YbWBpv2WKn11vpGryYyVSh`
    - Scheduler: Cloud-based scheduled trigger (Streamlit Cloud infrastructure)
    - Frequency: Every hour at :48 minutes past (UTC)
    - Database: Tracks analyzed message IDs by Message-ID header in `gmail_messages_analyzed` table
    - Config: `config.ini` (Gmail credentials, stored locally, not in git)
    """)

    col1, col2, col3 = st.columns([3, 1, 1])
    with col2:
        if st.button("[PLAY] Run Now", key="run_routine_1"):
            execute_routine("import_substack_imap.py", "Gmail Message Analysis")
    with col3:
        st.write("")

    st.divider()

    # Routine 2: Daily Institutional Data Import
    st.write("### [INSTITUTION] Routine 2: Daily Institutional Research Data Synthesis")
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.write("**Institutional APIs**")
    with col2:
        st.write("Daily")
    with col3:
        st.write("09:00 AM UTC")

    st.markdown("""
    **Data Sources:** NASA, NOAA, World Bank, FAO, CGIAR (direct API access, no webpage fetching) - analysis aligned with PROJECT GOALS

    **What It Does:**
    - NASA Earthdata: Temperature anomalies, precipitation, vegetation stress, sea level, Arctic ice
    - NOAA: Climate indicators, extreme weather events, ocean heat content
    - World Bank: Agricultural production, energy access, food import dependency, water stress, economic resilience
    - FAO: Food Price Index, agricultural production, supply/demand balances, crop failures, fertilizer availability
    - CGIAR: Water-energy-food nexus analysis, institutional interplay, cascade impact modeling
    - Maps institutional data streams to project goals for aligned signal extraction
    - Generates findings synthesized from multi-institutional data integration

    **Cascade Signals Generated:**
    - Climate stress indicators → Water system activation
    - Food price spikes → Feedback amplification node
    - Economic indicators → Geopolitical risk assessment
    - Infrastructure data → System brittleness tracking
    - Institutional coordination gaps → System failure nodes

    **Status:** [OK] Active (Cloud-Based)
    - Script: `import_institutional_data.py` (goal-driven analysis)
    - Trigger ID: `trig_01L8Ur1o577cLjUvpjcd2Jye`
    - Scheduler: Cloud-based scheduled trigger (Streamlit Cloud infrastructure)
    - Frequency: Daily at 09:00 UTC
    - No credentials needed (public institutional APIs)
    """)

    col1, col2, col3 = st.columns([3, 1, 1])
    with col2:
        if st.button("[PLAY] Run Now", key="run_routine_2"):
            execute_routine("import_institutional_data.py", "Institutional Data Import")
    with col3:
        st.write("")

    st.divider()

    # Routine 3: Daily Critical Infrastructure Monitoring
    st.write("### [WORLD] Routine 3: Daily Critical Infrastructure Monitoring")
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.write("**Global Infrastructure Data**")
    with col2:
        st.write("Daily")
    with col3:
        st.write("09:00 AM UTC")

    st.markdown("""
    **Data Sources:** Food security alerts, commodity markets, port congestion, grid incidents, water stress - analysis aligned with PROJECT GOALS

    **What It Does:**
    - FAO GIEWS: Food security alerts, crop failure regions, price spikes
    - Commodity Markets: Real-time grain, fertilizer, energy prices (daily snapshot)
    - Port Monitoring: Global shipping congestion, logistics bottlenecks
    - Water Stress Indicators: Regional water availability, drought conditions
    - Grid/Infrastructure: Major outages, supply chain disruptions
    - Maps infrastructure monitoring to project goals for aligned signal extraction
    - Generates synthesized findings from infrastructure data integration

    **Cascade Signals Generated:**
    - Food price volatility → Feedback amplification node
    - Supply chain delays → Economic node stress
    - Water availability collapse → Water system bifurcation
    - Energy infrastructure events → Cascading energy sector impacts
    - Fertilizer availability → Agricultural production node
    - Port disruptions → Infrastructure cascade node

    **Status:** [OK] Active (Cloud-Based)
    - Script: `import_daily_infrastructure.py` (goal-driven analysis)
    - Trigger ID: `trig_01MLpaPuRBMcL7RgXo7qgucW`
    - Scheduler: Cloud-based scheduled trigger (Streamlit Cloud infrastructure)
    - Frequency: Daily at 09:00 UTC
    - Data refresh: Daily (frequency sufficient for infrastructure-scale changes)
    """)

    col1, col2, col3 = st.columns([3, 1, 1])
    with col2:
        if st.button("[PLAY] Run Now", key="run_routine_3"):
            execute_routine("import_daily_infrastructure.py", "Daily Infrastructure Monitoring")
    with col3:
        st.write("")

    st.divider()

    st.subheader("Routine Summary & Management")

    # Summary table
    summary_data = {
        "Routine": ["Substack Email Import", "Institutional Data Import"],
        "Frequency": ["Daily", "Weekly"],
        "Time": ["08:00 AM", "Monday 10:00 AM"],
        "Sources": ["10 Substack researchers", "5 institutional APIs"],
        "Status": ["[OK] Active", "[OK] Ready"]
    }

    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("""
        | Routine | Frequency | Time | Sources | Status |
        |---------|-----------|------|---------|--------|
        | News Headline Scan | Hourly | :24 past hour | Multi-source news | [OK] Cloud-Based |
        | Gmail Message Analysis | Hourly | :48 past hour | All Gmail folders | [OK] Cloud-Based |
        | Infrastructure Monitoring | Daily | 09:00 AM UTC | FAO, markets, ports, water | [OK] Cloud-Based |
        | Institutional Data | Daily | 09:00 AM UTC | 5 institutional APIs | [OK] Cloud-Based |
        """)

    with col2:
        st.metric("Total Routines", "4")
        st.metric("Automation", "Cloud-based")

    st.divider()

    st.subheader("Data Pipeline Architecture")

    st.markdown("""
    **Your Design:**

    ```
    External Sources
    ├── Substack (10 researchers)
    │   └─→ Gmail IMAP
    │       └─→ import_substack_imap.py
    │
    └── Institutional APIs (NASA, NOAA, WB, FAO, CGIAR)
        └─→ import_institutional_data.py

    ↓ (Both pipelines)

    Cascade Signal Extraction
    ├── Keyword matching (cascade nodes)
    ├── Mechanism mapping (feedback loops, supply chain, etc.)
    └── Confidence scoring

    ↓

    cascade_db.py (SQLite)
    ├── signals table
    ├── findings table
    └── source attribution

    ↓

    Streamlit Dashboard (auto-update)
    ├── Research Findings page
    ├── System Dynamics visualization
    ├── Amplitude tracking
    └── Routines monitoring page (this page)
    ```

    **Result:** New cascade research appears automatically in your dashboard without any manual work
    """)

    st.divider()

    st.subheader("What You Designed")

    st.markdown("""
    **Your Requests → My Implementation:**

    1. **"Analyze all Gmail messages from all folders, not just Substack"**
       → Refactored `import_substack_imap.py` to scan ALL Gmail folders (PRIMARY, UPDATES, custom labels)
       → Added message tracking database to avoid re-analyzing messages by native Message-ID header
       → Extracts cascade signals from ANY email using goal-driven analysis aligned with project goals
       → Cloud-based hourly scheduler at :48 minutes past each hour (Routine 1)

    2. **"Real-time/ongoing monitoring of critical infrastructure developments globally with cascade implications"**
       → Built daily infrastructure monitoring pipeline (food, commodities, ports, water, grids) at 09:00 AM UTC (Routine 3)
       → Added hourly news headline scan for early warning of infrastructure incidents at :24 minutes past (Routine 0)
       → Cloud-based execution ensures continuous monitoring without local machine dependency

    3. **"This should not require your involvement / not depend on my Windows Task Scheduler"**
       → Migrated from local Windows Task Scheduler to cloud-based scheduled triggers on Streamlit Cloud infrastructure
       → All 4 routines now execute autonomously on the cloud without any local machine dependency
       → Routines: News (hourly :24), Gmail (hourly :48), Infrastructure (daily 09:00 UTC), Institutional (daily 09:00 UTC)

    4. **"Create a page documenting all the automated things/routines/searches/etc"**
       → Built this Routines page showing complete system architecture for all automated workflows
       → Includes trigger IDs, execution schedule, data sources, cascade value, and status

    5. **"Refactor routines to be goal-driven instead of keyword-driven"**
       → Refactored all 4 routines to load project goals at runtime and score content against goals
       → Each routine creates signals aligned with current project goals (scales dynamically as goals change)
       → Built `import_daily_news_headlines.py`, `import_substack_imap.py`, `import_institutional_data.py`, `import_daily_infrastructure.py` with goal-driven analysis

    6. **"Add hourly execution for news and Gmail routines"**
       → Cloud-based Routine 0 (News): executes hourly at :24 minutes past UTC
       → Cloud-based Routine 1 (Gmail): executes hourly at :48 minutes past UTC
       → Staggered execution prevents resource contention

    7. **"Try to be more proactive, I have no idea what you can do!"**
       → Now actively architecting and building all automation systems you'll need
    """)

    st.divider()

    st.subheader("Future Automation Opportunities")

    st.markdown("""
    **Ready to build (same level of automation):**

    1. **Enhanced Supply Chain Monitoring** (beyond daily snapshots)
       - Real-time semiconductor fab utilization (TSMC/Intel APIs if available)
       - AIS shipping data integration
       - Futures market volatility alerts

    2. **Advanced Climate Bifurcation Indicators**
       - Arctic methane emissions monitoring (daily alerts)
       - Greenland ice sheet velocity tracking
       - Atlantic Meridional Overturning Circulation (AMOC) strength

    3. **Geopolitical Risk Feeds**
       - Conflict event databases (daily monitoring)
       - Sanctions tracking
       - Migration flow data
       - Water disputes monitoring by region

    4. **Hyperlocal Infrastructure Alerts**
       - Major grid outages (incident monitoring)
       - Water system failures
       - Agricultural stress (via satellite soil moisture)

    5. **Social/Behavioral Early Warnings**
       - Search trend monitoring (shortages, panic buying signals)
       - Social media cascade sentiment analysis
       - Hoarding behavior detection (price elasticity anomalies)

    **Just ask.** I'll architect and implement full automation for any of these.
    """)

    st.divider()

    st.subheader("Standing Orders")

    st.markdown("""
    **Persistent Instructions That Apply Across All Sessions:**

    1. **Log all standing orders in this Routines documentation**
       - Any new standing order must be added to this section
       - Ensures continuity and visibility of persistent rules
       - Standing orders are accessible from the live dashboard

    2. **Keep cascade_app.py documentation synchronized with actual routine execution**
       - Treat cascade_app.py as the source of truth for routine configuration
       - Whenever any routine changes (frequency, trigger ID, data source, status), update BOTH:
         * The corresponding routine's markdown section in this page
         * The summary table showing all routines at a glance
       - This ensures the documentation always reflects actual cloud execution
       - Changes to routines should prompt immediate updates to this page
    """)

    st.divider()

    st.subheader("Technical Notes")

    with st.expander("Routine Configuration Details"):
        st.markdown("""
        **Cloud-Based Routine Execution (Gmail Analysis Example):**
        ```
        1. Cloud Scheduled Trigger fires at :48 minutes past each hour (UTC)
           - Trigger ID: trig_01YbWBpv2WKn11vpGryYyVSh
           - Schedule: 48 * * * * (every hour at :48 past)
        2. Launches: python import_substack_imap.py in fresh cloud session
        3. Reads credentials from config.ini (stored locally on cloud)
        4. Connects to Gmail IMAP server
        5. Queries ALL Gmail folders (PRIMARY, UPDATES, custom labels, etc.)
        6. For each unanalyzed email (by Message-ID):
           - Extract subject, body, sender, date, folder
           - Score against project goals (goal-driven analysis)
           - Map to cascade nodes based on goal alignment
           - Create signals and findings
           - Store in cascade_data.db
        7. Update gmail_messages_analyzed table with Message-ID (prevent re-analysis)
        8. Task completes, awaits next hourly trigger
        ```

        **Database Impact:**
        - Signals table: New entries per email analyzed
        - Findings table: New findings per goal-relevant content
        - gmail_messages_analyzed table: Track analyzed Message-IDs
        - Source attribution: Email folder, sender, subject
        - Automatic timestamp: Current run date/time UTC

        **Failure Handling:**
        - Cloud logs errors to trigger execution history
        - Failed runs don't block subsequent hourly runs
        - Manual re-run possible anytime via Run Now button or trigger API
        """)

    with st.expander("Adding New Routines"):
        st.markdown("""
        To add a new automated routine (cloud-based):

        1. **Create a Python script** that:
           - Loads project goals via get_all_goals() (for goal-driven analysis)
           - Connects to data source (API, database, email, etc.)
           - Extracts relevant data and scores against project goals
           - Maps findings to cascade nodes based on goal alignment
           - Calls add_signal() and add_finding() to persist results

        2. **Test manually** first to verify data extraction and goal alignment works

        3. **Deploy to cloud**:
           - Push script to GitHub (auto-deploys to Streamlit Cloud within 1-2 minutes)
           - Verify script executes successfully on cloud

        4. **Create cloud-based scheduled trigger**:
           - Use mcp__claude-code-remote__create_trigger tool
           - Specify cron expression (e.g., "0 * * * *" for hourly, "0 9 * * *" for daily 09:00 UTC)
           - Trigger automatically calls script at scheduled time
           - No Task Scheduler or local machine dependency required

        5. **Document** in this Routines page with:
           - Trigger ID
           - Schedule and frequency (cron expression)
           - Data source and goal mapping
           - Cascade mechanism outputs
           - Status (Active / Cloud-Based)

        6. **Monitor** via trigger execution history in cloud dashboard and dashboard signal updates
        """)

# ============================================
# MAIN APP
# ============================================
def main():
    # Sidebar navigation
    with st.sidebar:
        st.title("Project Cascade")
        st.markdown("---")

        sections = [
            "Summary",
            "Today's Progress",
            "Research Findings",
            "Project Goals",
            "System Dynamics",
            "Threat Landscape",
            "Supply Chain Constraints",
            "Solutions & Horizon",
            "Strategic Blind Spots",
            "Global Infrastructure Watch",
            "Policy Gap Analysis",
            "Bifurcation Point",
            "System Mechanism Tracker",
            "Amplitude",
            "Cascading Nodes Visualizing",
            "Systematic Underestimation",
            "Granularity",
            "Appendix",
            "Routines"
        ]

        selected = st.radio("Navigation", sections, label_visibility="collapsed")

    # Main content
    if selected == "Research Findings":
        section_findings()
    elif selected == "System Dynamics":
        section_system_dynamics()
    elif selected == "Threat Landscape":
        section_threat_landscape()
    elif selected == "Supply Chain Constraints":
        section_supply_chain_constraints()
    elif selected == "Solutions & Horizon":
        section_solutions_horizon()
    elif selected == "Strategic Blind Spots":
        section_strategic_blind_spots()
    elif selected == "Global Infrastructure Watch":
        section_global_infrastructure_watch()
    elif selected == "Policy Gap Analysis":
        section_policy_gap_analysis()
    elif selected == "Bifurcation Point":
        section_bifurcation_point()
    elif selected == "Summary":
        section_summary()
    elif selected == "Today's Progress":
        section_today_progress()
    elif selected == "System Mechanism Tracker":
        section_system_mechanism_tracker()
    elif selected == "Project Goals":
        section_project_goals()
    elif selected == "Amplitude":
        section_amplitude()
    elif selected == "Cascading Nodes Visualizing":
        section_cascading_nodes()
    elif selected == "Systematic Underestimation":
        section_systematic_underestimation()
    elif selected == "Granularity":
        section_granularity()
    elif selected == "Appendix":
        section_appendix()
    elif selected == "Routines":
        section_routines()

    # Footer
    st.divider()
    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == '__main__':
    main()
