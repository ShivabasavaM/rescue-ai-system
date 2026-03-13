import streamlit as st
import pandas as pd
import json
import os
import time
from filelock import FileLock

st.set_page_config(page_title="Rescue Dispatch", page_icon="🏥", layout="wide")
st.title("🏥 Central Dispatch | Rescue Triage")
st.markdown("Live incident queue powered by asynchronous Webhooks and MobileNetV3 Triage.")

LOG_FILE = "dispatch_log.json"
LOCK_FILE = "dispatch_log.json.lock"

# --- Secure File Operations ---
def load_data():
    if not os.path.exists(LOG_FILE) or os.path.getsize(LOG_FILE) == 0:
        return []
    try:
        with FileLock(LOCK_FILE, timeout=2):
            with open(LOG_FILE, "r") as f:
                return json.load(f)
    except Exception:
        return [] 

def save_data(data):
    with FileLock(LOCK_FILE, timeout=2):
        with open(LOG_FILE, "w") as f:
            json.dump(data, f, indent=4)

def mark_dispatched(incident_id):
    data = load_data()
    for entry in data:
        if entry.get("incident_id") == incident_id:
            entry["status"] = "dispatched"
    save_data(data)
    st.toast(f"Unit dispatched for {incident_id}!", icon="✅")

# --- Process Data ---
logs = load_data()
active_logs = [log for log in logs if log.get('status') != 'dispatched']
history_logs = [log for log in logs if log.get('status') == 'dispatched']

# --- Analytics Dashboard ---
col1, col2, col3 = st.columns(3)
critical_count = sum(1 for log in active_logs if log.get('priority_level') == 'Critical')
safe_count = sum(1 for log in active_logs if log.get('priority_level') == 'Safe')

with col1:
    st.metric("Total Active Incidents", len(active_logs))
with col2:
    st.metric("🔴 Critical (Pending)", critical_count)
with col3:
    st.metric("🟢 Safe (Pending)", safe_count)
    
st.divider()

# --- Tabbed Interface ---
tab1, tab2 = st.tabs(["🚨 Active Triage Queue", "🗄️ Incident History"])

with tab1:
    if not active_logs:
        st.info("📭 Queue is clear. All units dispatched or no active emergencies.")
    else:
        h1, h2, h3, h4 = st.columns([2, 3, 3, 3])
        h1.markdown("**Incident ID**")
        h2.markdown("**AI Priority Classification**")
        h3.markdown("**Current Status**")
        h4.markdown("**Action**")
        st.markdown("---")
        
        for alert in active_logs:
            c1, c2, c3, c4 = st.columns([2, 3, 3, 3])
            c1.code(alert['incident_id'])
            
            if alert.get('priority_level') == "Critical":
                c2.error("🔴 CRITICAL DISPATCH")
            else:
                c2.success("🟢 SAFE / MONITOR")
                
            c3.markdown(f"*{alert.get('status', 'pending_dispatch').replace('_', ' ').title()}*")
            
            if c4.button("🚀 Dispatch Field Unit", key=f"btn_{alert['incident_id']}", use_container_width=True):
                mark_dispatched(alert['incident_id'])
                st.rerun()

with tab2:
    if not history_logs:
        st.write("No historical data available yet.")
    else:
        # Create a clean DataFrame for the historical audit log
        history_df = pd.DataFrame(history_logs)
        history_df = history_df.rename(columns={
            "incident_id": "Incident ID",
            "priority_level": "Priority Level",
            "status": "Final Status"
        })
        # Rearrange columns to put ID first
        cols = ["Incident ID", "Priority Level", "Final Status"]
        if "critical_confidence" in history_df.columns:
            history_df = history_df.rename(columns={"critical_confidence": "AI Confidence"})
            cols.append("AI Confidence")
            
        history_df = history_df[[c for c in cols if c in history_df.columns]]
        st.dataframe(history_df, use_container_width=True, hide_index=True)

time.sleep(4)
st.rerun()